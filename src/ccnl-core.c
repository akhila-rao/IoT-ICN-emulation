/*
 * @f ccnl-core.c
 * @b CCN lite, core CCNx protocol logic
 *
 * Copyright (C) 2011-15, Christian Tschudin, University of Basel
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 * File history:
 * 2011-04-09 created
 * 2013-10-12 add crypto support <christopher.scherb@unibas.ch>
 * 2014-03-20 started to move ccnx (pre 2014) specific routines to "fwd-ccnb.c"
 */


#ifndef USE_NFN
# define ccnl_nfn_interest_remove(r,i)  ccnl_interest_remove(r,i)
#endif

// forward reference:
void ccnl_face_CTS(struct ccnl_relay_s *ccnl, struct ccnl_face_s *f);
int ccnl_prefix_cmp(struct ccnl_prefix_s *name, unsigned char *md,
                    struct ccnl_prefix_s *p, int mode);
int ccnl_i_prefixof_c(struct ccnl_prefix_s *prefix, int minsuffix,
                      int maxsuffix, struct ccnl_content_s *c);

// ----------------------------------------------------------------------
// datastructure support functions

#define buf_dup(B)      (B) ? ccnl_buf_new(B->data, B->datalen) : NULL
#define buf_equal(X,Y)  ((X) && (Y) && (X->datalen==Y->datalen) &&\
                         !memcmp(X->data,Y->data,X->datalen))

struct ccnl_prefix_s* ccnl_prefix_new(int suite, int cnt);

int findIntFromStr(char * s1, char* delim);

void squareOfMatrix(double mat[2][2]){
        int i=0,j=0,k=0;
        int m=2;
        double sum=0;
        double sqr[2][2]= {{0}};

        for(i=0;i<m;i++)
                for(j=0;j<m;j++)
                        sqr[i][j]=0;

        for(i=0;i<m;i++){ //row of first matrix
                for(j=0;j<m;j++){  //column of second matrix
                        sum=0;
                        for(k=0;k<m;k++)
                                sum=sum+mat[i][k]*mat[k][j];
                                sqr[i][j]=sum;
                }
        }

        for(i=0;i<m;i++){
                for(j=0;j<m;j++){
                        mat[i][j] = sqr[i][j];
                }
        }

}



int drop_this_pkt(struct ccnl_relay_s *relay, struct ccnl_face_s *from){
        int drop = 0;
#ifdef USE_LOSSY_LINKS
	int from_nodeID = findIntFromStr(ccnl_addr2ascii(from ? &from->peer : NULL),"/") - 9000;	// NULL here means there is something wrong
        int my_nodeID = relay->nodeID;
//        DEBUGMSG_CORE(DEBUG, " ICNIoT: pkt received at node %d from node %d\n",my_nodeID, from_nodeID);

        int* ptr = relay->network_links_ptr;
        int j=0;
        int flag = 0;
        for(j=0;j<relay->num_of_links;j++){
            if(((*(ptr + 2*j) == from_nodeID) && (*(ptr + 2*j +1) == my_nodeID)) || ((*(ptr + 2*j) == my_nodeID) && (*(ptr + 2*j +1) == from_nodeID))){// this implies that we are checking bidirectional links
                flag =1;
                break;
             }
        }
        if(flag==0){
//           DEBUGMSG_CORE(DEBUG, " ICNIoT: This link is NOT a lossy link\n");
           return 0;
        }

//        DEBUGMSG_CORE(DEBUG, " ICNIoT: This link is a lossy link\n");

	double P[2][2];
	P[0][0] = (double)1-(double)ALPHA;
	P[0][1] = (double)ALPHA;
	P[1][0] = (double)BETA;
	P[1][1] = (double)1-(double)BETA;
	// 100 ms is one step 
	double val;
	int i=0;
        j=0;
//        int m=2;
	int n = (int)(((CCNL_NOW() - relay->last_pkt_recv_time)*(double)STEP_SCALE) + 1);
//        DEBUGMSG_CORE(DEBUG, " ICNIoT: number of steps passed since last pkt receive is %f - %f = %d\n",CCNL_NOW(),relay->last_pkt_recv_time,n);
	if (n > 20)// This 20 is because when n is large, due to loss of accuracy the P^n matrix either becomes all 0s or inf
		n=20;

	for(i=0;i<n;i++)
		squareOfMatrix(P);

//	printf("P^%d is \n",n);
//        for(i=0;i<m;i++){
//                for(j=0;j<m;j++){
//                        printf("%f ",P[i][j]);
//                }
//		printf("\n");
//        }

	val = P[relay->last_state][0];
//        DEBUGMSG_CORE(DEBUG, " ICNIoT: current state is %d\n",relay->last_state);
        double rnd = (double)rand() / (double)((unsigned)RAND_MAX + 1);  
        if(rnd < val)
		relay->last_state = 0; //update state
	else relay->last_state = 1; // update state


        rnd = (double)rand() / (double)((unsigned)RAND_MAX + 1);
//	DEBUGMSG_CORE(DEBUG, " ICNIoT: Next state is %d, using error rate = %f\n",relay->last_state, relay->linkErrProb[relay->last_state]);
	if(rnd < relay->linkErrProb[relay->last_state])
                drop =1;


	relay->last_pkt_recv_time = CCNL_NOW();
#endif
        return drop;
}


// ----------------------------------------------------------------------
// addresses, interfaces and faces

int
ccnl_addr_cmp(sockunion *s1, sockunion *s2)
{
    if (s1->sa.sa_family != s2->sa.sa_family)
        return -1;
    switch (s1->sa.sa_family) {
#ifdef USE_ETHERNET
        case AF_PACKET:
            return memcmp(s1->eth.sll_addr, s2->eth.sll_addr, ETH_ALEN);
#endif
#ifdef USE_IPV4
        case AF_INET:
            return s1->ip4.sin_addr.s_addr == s2->ip4.sin_addr.s_addr &&
                        s1->ip4.sin_port == s2->ip4.sin_port ? 0 : -1;
#endif
#ifdef USE_UNIXSOCKET
        case AF_UNIX:
            return strcmp(s1->ux.sun_path, s2->ux.sun_path);
#endif
        default:
            break;
    }
    return -1;
}

struct ccnl_face_s*
ccnl_get_face_or_create(struct ccnl_relay_s *ccnl, int ifndx,
                       struct sockaddr *sa, int addrlen)
// sa==NULL means: local(=in memory) client, search for existing ifndx being -1
// sa!=NULL && ifndx==-1: search suitable interface for given sa_family
// sa!=NULL && ifndx!=-1: use this (incoming) interface for outgoing
{
    static int seqno;
    int i;
    struct ccnl_face_s *f;

    DEBUGMSG_CORE(TRACE, "ccnl_get_face_or_create src=%s\n",
             ccnl_addr2ascii((sockunion*)sa));

    for (f = ccnl->faces; f; f = f->next) {
        if (!sa) {
            if (f->ifndx == -1)
                return f;
            continue;
        }
        if (ifndx != -1 && !ccnl_addr_cmp(&f->peer, (sockunion*)sa)) {
            f->last_used = CCNL_NOW();
            return f;
        }
    }

    if (sa && ifndx == -1) {
        for (i = 0; i < ccnl->ifcount; i++) {
            if (sa->sa_family != ccnl->ifs[i].addr.sa.sa_family)
                continue;
            ifndx = i;
            break;
        }
        if (ifndx == -1) // no suitable interface found
            return NULL;
    }
    DEBUGMSG_CORE(VERBOSE, "  found suitable interface %d for %s\n", ifndx,
                ccnl_addr2ascii((sockunion*)sa));

    f = (struct ccnl_face_s *) ccnl_calloc(1, sizeof(struct ccnl_face_s));
    if (!f) {
        DEBUGMSG_CORE(VERBOSE, "  no memory for face\n");
        return NULL;
    }
    f->faceid = ++seqno;
    f->ifndx = ifndx;

    if (ifndx >= 0) {
        if (ccnl->defaultFaceScheduler)
            f->sched = ccnl->defaultFaceScheduler(ccnl,
                                          (void(*)(void*,void*))ccnl_face_CTS);
        if (ccnl->ifs[ifndx].reflect)   f->flags |= CCNL_FACE_FLAGS_REFLECT;
        if (ccnl->ifs[ifndx].fwdalli)   f->flags |= CCNL_FACE_FLAGS_FWDALLI;
    }

    if (sa)
        memcpy(&f->peer, sa, addrlen);
    else // local client
        f->ifndx = -1;
    f->last_used = CCNL_NOW();
    DBL_LINKED_LIST_ADD(ccnl->faces, f);

    TRACEOUT();
    return f;
}

struct ccnl_face_s*
ccnl_face_remove(struct ccnl_relay_s *ccnl, struct ccnl_face_s *f)
{
    struct ccnl_face_s *f2;
    struct ccnl_interest_s *pit;
    struct ccnl_forward_s **ppfwd;

    DEBUGMSG_CORE(DEBUG, "face_remove relay=%p face=%p\n",
             (void*)ccnl, (void*)f);

    ccnl_sched_destroy(f->sched);
    ccnl_frag_destroy(f->frag);

    DEBUGMSG_CORE(TRACE, "face_remove: cleaning PIT\n");
    for (pit = ccnl->pit; pit; ) {
        struct ccnl_pendint_s **ppend, *pend;
        if (pit->from == f)
            pit->from = NULL;
        for (ppend = &pit->pending; *ppend;) {
            if ((*ppend)->face == f) {
                pend = *ppend;
                *ppend = pend->next;
                ccnl_free(pend);
            } else
                ppend = &(*ppend)->next;
        }
        if (pit->pending)
            pit = pit->next;
        else {
            DEBUGMSG_CORE(TRACE, "before NFN interest_remove 0x%p\n",
                          (void*)pit);
            pit = ccnl_nfn_interest_remove(ccnl, pit);
        }
    }
    DEBUGMSG_CORE(TRACE, "face_remove: cleaning fwd table\n");
    for (ppfwd = &ccnl->fib; *ppfwd;) {
        if ((*ppfwd)->face == f) {
            struct ccnl_forward_s *pfwd = *ppfwd;
            free_prefix(pfwd->prefix);
            *ppfwd = pfwd->next;
            ccnl_free(pfwd);
        } else
            ppfwd = &(*ppfwd)->next;
    }
    DEBUGMSG_CORE(TRACE, "face_remove: cleaning pkt queue\n");
    while (f->outq) {
        struct ccnl_buf_s *tmp = f->outq->next;
        ccnl_free(f->outq);
        f->outq = tmp;
    }
    DEBUGMSG_CORE(TRACE, "face_remove: unlinking1 %p %p\n",
             (void*)f->next, (void*)f->prev);
    f2 = f->next;
    DEBUGMSG_CORE(TRACE, "face_remove: unlinking2\n");
    DBL_LINKED_LIST_REMOVE(ccnl->faces, f);
    DEBUGMSG_CORE(TRACE, "face_remove: unlinking3\n");
    ccnl_free(f);

    TRACEOUT();
    return f2;
}

void
ccnl_interface_cleanup(struct ccnl_if_s *i)
{
    int j;
    DEBUGMSG_CORE(TRACE, "ccnl_interface_cleanup\n");

    ccnl_sched_destroy(i->sched);
    for (j = 0; j < i->qlen; j++) {
        struct ccnl_txrequest_s *r = i->queue + (i->qfront+j)%CCNL_MAX_IF_QLEN;
        ccnl_free(r->buf);
    }
    ccnl_close_socket(i->sock);
}

// ----------------------------------------------------------------------
// face and interface queues, scheduling

void
ccnl_interface_CTS(void *aux1, void *aux2)
{
    struct ccnl_relay_s *ccnl = (struct ccnl_relay_s *)aux1;
    struct ccnl_if_s *ifc = (struct ccnl_if_s *)aux2;
    struct ccnl_txrequest_s *r, req;

    DEBUGMSG_CORE(TRACE, "interface_CTS interface=%p, qlen=%d, sched=%p\n",
             (void*)ifc, ifc->qlen, (void*)ifc->sched);

    if (ifc->qlen <= 0)
        return;

#ifdef USE_STATS
    ifc->tx_cnt++;
#endif

    r = ifc->queue + ifc->qfront;
    memcpy(&req, r, sizeof(req));
    ifc->qfront = (ifc->qfront + 1) % CCNL_MAX_IF_QLEN;
    ifc->qlen--;

    ccnl_ll_TX(ccnl, ifc, &req.dst, req.buf);
#ifdef USE_SCHEDULER
    ccnl_sched_CTS_done(ifc->sched, 1, req.buf->datalen);
    if (req.txdone)
        req.txdone(req.txdone_face, 1, req.buf->datalen);
#endif
    ccnl_free(req.buf);
}

void
ccnl_interface_enqueue(void (tx_done)(void*, int, int), struct ccnl_face_s *f,
                       struct ccnl_relay_s *ccnl, struct ccnl_if_s *ifc,
                       struct ccnl_buf_s *buf, sockunion *dest)
{
    struct ccnl_txrequest_s *r;

    DEBUGMSG_CORE(TRACE, "enqueue interface=%p buf=%p len=%d (qlen=%d)\n",
                  (void*)ifc, (void*)buf,
                  buf ? buf->datalen : -1, ifc ? ifc->qlen : -1);

    if (ifc->qlen >= CCNL_MAX_IF_QLEN) {
        DEBUGMSG_CORE(WARNING, "  DROPPING buf=%p\n", (void*)buf);
        ccnl_free(buf);
        return;
    }
    r = ifc->queue + ((ifc->qfront + ifc->qlen) % CCNL_MAX_IF_QLEN);
    r->buf = buf;
    memcpy(&r->dst, dest, sizeof(sockunion));
    r->txdone = tx_done;
    r->txdone_face = f;
    ifc->qlen++;

#ifdef USE_SCHEDULER
    ccnl_sched_RTS(ifc->sched, 1, buf->datalen, ccnl, ifc);
#else
    ccnl_interface_CTS(ccnl, ifc);
#endif
}

struct ccnl_buf_s*
ccnl_face_dequeue(struct ccnl_relay_s *ccnl, struct ccnl_face_s *f)
{
    struct ccnl_buf_s *pkt;
    DEBUGMSG_CORE(TRACE, "dequeue face=%p (id=%d.%d)\n",
             (void *) f, ccnl->id, f->faceid);

    if (!f->outq)
        return NULL;
    pkt = f->outq;
    f->outq = pkt->next;
    if (!pkt->next)
        f->outqend = NULL;
    pkt->next = NULL;
    return pkt;
}

void
ccnl_face_CTS_done(void *ptr, int cnt, int len)
{
    DEBUGMSG_CORE(TRACE, "CTS_done face=%p cnt=%d len=%d\n", ptr, cnt, len);

#ifdef USE_SCHEDULER
    struct ccnl_face_s *f = (struct ccnl_face_s*) ptr;
    ccnl_sched_CTS_done(f->sched, cnt, len);
#endif
}

void
ccnl_face_CTS(struct ccnl_relay_s *ccnl, struct ccnl_face_s *f)
{
    struct ccnl_buf_s *buf;
    DEBUGMSG_CORE(TRACE, "CTS face=%p sched=%p\n", (void*)f, (void*)f->sched);

    if (!f->frag || f->frag->protocol == CCNL_FRAG_NONE) {
        buf = ccnl_face_dequeue(ccnl, f);
        if (buf)
            ccnl_interface_enqueue(ccnl_face_CTS_done, f,
                                   ccnl, ccnl->ifs + f->ifndx, buf, &f->peer);
    }
#ifdef USE_FRAG
    else {
        sockunion dst;
        int ifndx = f->ifndx;
        buf = ccnl_frag_getnext(f->frag, &ifndx, &dst);
        if (!buf) {
            buf = ccnl_face_dequeue(ccnl, f);
            ccnl_frag_reset(f->frag, buf, f->ifndx, &f->peer);
            buf = ccnl_frag_getnext(f->frag, &ifndx, &dst);
        }
        if (buf) {
            ccnl_interface_enqueue(ccnl_face_CTS_done, f,
                                   ccnl, ccnl->ifs + ifndx, buf, &dst);
#ifndef USE_SCHEDULER
            ccnl_face_CTS(ccnl, f); // loop to push more fragments
#endif
        }
    }
#endif
}

int
ccnl_face_enqueue(struct ccnl_relay_s *ccnl, struct ccnl_face_s *to,
                 struct ccnl_buf_s *buf)
{
    struct ccnl_buf_s *msg;
    DEBUGMSG_CORE(TRACE, "enqueue face=%p (id=%d.%d) buf=%p len=%d\n",
             (void*) to, ccnl->id, to->faceid, (void*) buf, buf ? buf->datalen : -1);

    for (msg = to->outq; msg; msg = msg->next) // already in the queue?
        if (buf_equal(msg, buf)) {
            DEBUGMSG_CORE(VERBOSE, "    not enqueued because already there\n");
            ccnl_free(buf);
            return -1;
        }
    buf->next = NULL;
    if (to->outqend)
        to->outqend->next = buf;
    else
        to->outq = buf;
    to->outqend = buf;
#ifdef USE_SCHEDULER
    if (to->sched) {
#ifdef USE_FRAG
        int len, cnt = ccnl_frag_getfragcount(to->frag, buf->datalen, &len);
#else
        int len = buf->datalen, cnt = 1;
#endif
        ccnl_sched_RTS(to->sched, cnt, len, ccnl, to);
    } else
        ccnl_face_CTS(ccnl, to);
#else
    ccnl_face_CTS(ccnl, to);
#endif

    return 0;
}

// ----------------------------------------------------------------------
// handling of interest messages

struct ccnl_interest_s*
ccnl_interest_new(struct ccnl_relay_s *ccnl, struct ccnl_face_s *from,
                  struct ccnl_pkt_s **pkt)
{
    struct ccnl_interest_s *i = (struct ccnl_interest_s *) ccnl_calloc(1,
                                            sizeof(struct ccnl_interest_s));
    DEBUGMSG_CORE(TRACE, "ccnl_new_interest\n");
             //             ccnl_prefix_to_path((*pkt)->pfx),
             //             ccnl_suite2str((*pkt)->pfx->suite));

    if (!i)
        return NULL;
    i->pkt = *pkt;
    *pkt = NULL;
    i->flags |= CCNL_PIT_COREPROPAGATES;
    i->from = from;
    i->last_used = CCNL_NOW();
    DBL_LINKED_LIST_ADD(ccnl->pit, i);
//akhila 16-10-2015
    ccnl->pitcnt++;
    DEBUGMSG_CORE(TRACE, ": pit_entry_added:%d\n",ccnl->pitcnt);
    return i;
}

int
ccnl_interest_append_pending(struct ccnl_interest_s *i,
                             struct ccnl_face_s *from)
{
    struct ccnl_pendint_s *pi, *last = NULL;
    DEBUGMSG_CORE(TRACE, "ccnl_append_pending\n");

    for (pi = i->pending; pi; pi = pi->next) { // check whether already listed
        if (pi->face == from) {
            DEBUGMSG_CORE(DEBUG, "  we found a matching interest, updating time\n");
            pi->last_used = CCNL_NOW();
            return 0;
        }
        last = pi;
    }
    pi = (struct ccnl_pendint_s *) ccnl_calloc(1,sizeof(struct ccnl_pendint_s));
    if (!pi) {
        DEBUGMSG_CORE(DEBUG, "  no mem\n");
        return -1;
    }
    DEBUGMSG_CORE(DEBUG, "  appending a new face entry to pendint entry %p\n", (void *) pi);
    pi->face = from;
    pi->last_used = CCNL_NOW();
    if (last)
        last->next = pi;
    else
        i->pending = pi;
    return 0;
}

void
ccnl_interest_propagate(struct ccnl_relay_s *ccnl, struct ccnl_interest_s *i)
{
    struct ccnl_forward_s *fwd;
    int rc = 0;
#ifdef USE_NACK
    int matching_face = 0;
#endif

    if (!i)
        return;
    DEBUGMSG_CORE(DEBUG, "ccnl_interest_propagate\n");

    // CONFORM: "A node MUST implement some strategy rule, even if it is only to
    // transmit an Interest Message on all listed dest faces in sequence."
    // CCNL strategy: we forward on all FWD entries with a prefix match

    for (fwd = ccnl->fib; fwd; fwd = fwd->next) {
        if (!fwd->prefix)
            continue;

        //Only for matching suite
        if (!i->pkt->pfx || fwd->suite != i->pkt->pfx->suite) {
            DEBUGMSG_CORE(VERBOSE, "  not same suite (%d/%d)\n",
                     fwd->suite, i->pkt->pfx ? i->pkt->pfx->suite : -1);
            continue;
        }

        rc = ccnl_prefix_cmp(fwd->prefix, NULL, i->pkt->pfx, CMP_LONGEST);

//        DEBUGMSG_CORE(DEBUG, "  ccnl_interest_propagate, rc=%d/%d\n",
//                 rc, fwd->prefix->compcnt);
        if (rc < fwd->prefix->compcnt)
            continue;

//        DEBUGMSG_CORE(DEBUG, "  ccnl_interest_propagate, fwd==%p\n", (void*)fwd);
        // suppress forwarding to origin of interest, except wireless
        if (!i->from || fwd->face != i->from ||
                                (i->from->flags & CCNL_FACE_FLAGS_REFLECT)) {
//            DEBUGMSG_CFWD(INFO, "  outgoing interest=<%s> to=%s\n",
//                          ccnl_prefix_to_path(i->pkt->pfx),
//                          fwd->face ? ccnl_addr2ascii(&fwd->face->peer)
//                                    : "<tap>");
            DEBUGMSG_CORE(INFO, " ICNIoT: outgoing_interest\n");
            ccnl_nfn_monitor(ccnl, fwd->face, i->pkt->pfx, NULL, 0);

            // DEBUGMSG(DEBUG, "%p %p %p\n", (void*)i, (void*)i->pkt, (void*)i->pkt->buf);
            if (fwd->tap)
                (fwd->tap)(ccnl, i->from, i->pkt->pfx, i->pkt->buf);
            if (fwd->face)
                ccnl_face_enqueue(ccnl, fwd->face, buf_dup(i->pkt->buf));

#ifdef USE_NACK
            matching_face = 1;
#endif
        } else {
            DEBUGMSG_CORE(DEBUG, "  not forwarded\n");
        }
    }

#ifdef USE_NACK
    if(!matching_face){
        ccnl_nack_reply(ccnl, i->pkt->pfx, i->from, i->pkt->pfx->suite);
        ccnl_interest_remove(ccnl, i);
    }
#endif

    return;
}

struct ccnl_interest_s*
ccnl_interest_remove(struct ccnl_relay_s *ccnl, struct ccnl_interest_s *i)
{
    struct ccnl_interest_s *i2;

/*
    if (!i)
        return NULL;
*/
    DEBUGMSG_CORE(TRACE, "ccnl_interest_remove %p\n", (void *) i);
//akhila 16-10-2015
    ccnl->pitcnt--;
    DEBUGMSG_CORE(TRACE, ": pit_entry_removed:%d\n",ccnl->pitcnt);

/*
#ifdef USE_NFN
    if (!(i->flags & CCNL_PIT_COREPROPAGATES))
        return i->next;
#endif
*/
    while (i->pending) {
        struct ccnl_pendint_s *tmp = i->pending->next;
        ccnl_free(i->pending);
        i->pending = tmp;
    }
    i2 = i->next;
    DBL_LINKED_LIST_REMOVE(ccnl->pit, i);


    free_packet(i->pkt);
    ccnl_free(i);
    return i2;
}

int
ccnl_interest_isSame(struct ccnl_interest_s *i, struct ccnl_pkt_s *pkt)
{
    if (i->pkt->pfx->suite != pkt->suite ||
                ccnl_prefix_cmp(i->pkt->pfx, NULL, pkt->pfx, CMP_EXACT))
        return 0;

    switch (i->pkt->pfx->suite) {
#ifdef USE_SUITE_CCNB
    case CCNL_SUITE_CCNB:
        return i->pkt->s.ccnb.minsuffix == pkt->s.ccnb.minsuffix &&
               i->pkt->s.ccnb.maxsuffix == pkt->s.ccnb.maxsuffix &&
               ((!i->pkt->s.ccnb.ppkd && !pkt->s.ccnb.ppkd) ||
                    buf_equal(i->pkt->s.ccnb.ppkd, pkt->s.ccnb.ppkd));
#endif
#ifdef USE_SUITE_NDNTLV
    case CCNL_SUITE_NDNTLV:
        return i->pkt->s.ndntlv.minsuffix == pkt->s.ndntlv.minsuffix &&
               i->pkt->s.ndntlv.maxsuffix == pkt->s.ndntlv.maxsuffix &&
               ((!i->pkt->s.ndntlv.ppkl && !pkt->s.ndntlv.ppkl) ||
                    buf_equal(i->pkt->s.ndntlv.ppkl, pkt->s.ndntlv.ppkl));
#endif
#ifdef USE_SUITE_CCNTLV
    case CCNL_SUITE_CCNTLV:
#endif
#ifdef USE_SUITE_CISTLV
    case CCNL_SUITE_CISTLV:
#endif
#ifdef USE_SUITE_IOTTLV
    case CCNL_SUITE_IOTTLV:
#endif
    default:
        break;
    }
    return 1;
}

// ----------------------------------------------------------------------
// handling of content messages

struct ccnl_content_s*
ccnl_content_new(struct ccnl_relay_s *ccnl, struct ccnl_pkt_s **pkt)
{
    struct ccnl_content_s *c;

//    DEBUGMSG_CORE(TRACE, "ccnl_content_new %p <%s [%d]>\n",
//             (void*) *pkt, ccnl_prefix_to_path((*pkt)->pfx), ((*pkt)->pfx->chunknum)? *((*pkt)->pfx->chunknum) : -1);

    c = (struct ccnl_content_s *) ccnl_calloc(1, sizeof(struct ccnl_content_s));
    if (!c)
        return NULL;
    c->pkt = *pkt;
    *pkt = NULL;
    c->last_used = CCNL_NOW();
    c->recommended_cache_time = CCNL_NOW() + PUBLISHING_TIMEPERIOD;
    return c;
}

struct ccnl_content_s*
ccnl_content_remove(struct ccnl_relay_s *ccnl, struct ccnl_content_s *c)
{
    struct ccnl_content_s *c2;
    c2 = c->next;
    DBL_LINKED_LIST_REMOVE(ccnl->contents, c);

//    free_content(c);
    if (c->pkt) {
        free_prefix(c->pkt->pfx);
        ccnl_free(c->pkt->buf);
        ccnl_free(c->pkt);
    }
    //    free_prefix(c->name);
    ccnl_free(c);

    ccnl->contentcnt--;
    DEBUGMSG_CORE(INFO, " ICNIoT: remove_contentFromCache:%d\n",ccnl->contentcnt);
    return c2;
}

#ifdef UPDATE_TIME_SERIES
int IsTimeSeriesContent(struct ccnl_prefix_s *pfx){
    int skip=4;
    int i=0;
    char *str1 ="sq=";
    for(i = 0; i < pfx->compcnt; ++i){
        if(!memcmp(pfx->comp[i]+skip, str1, strlen(str1)))
            return 1;
    }
    return 0;
}

struct ccnl_content_s * 
findOlderVersion(struct ccnl_relay_s *ccnl, struct ccnl_prefix_s *newCOpfx){
    int skip =4;
    struct ccnl_content_s *cit;
    struct ccnl_content_s *oldVersionCO;
    struct ccnl_prefix_s *oldVersionPfx;
    int i=0;
    char *str1 ="sq=";
    oldVersionCO =  NULL;
    oldVersionPfx = newCOpfx;

    for (cit = ccnl->contents; cit; cit = cit->next) {// each content in CS
        for(i = 0; i < oldVersionPfx->compcnt; ++i) {// each component of each content object prefix
            if(memcmp(oldVersionPfx->comp[i]+skip,cit->pkt->pfx->comp[i]+skip,oldVersionPfx->complen[i]) != 0){
                if(!memcmp(cit->pkt->pfx->comp[i]+skip,str1,strlen(str1)) && !memcmp(oldVersionPfx->comp[i]+skip,str1,strlen(str1)) &&
(findIntFromStr((char *)oldVersionPfx->comp[i]+skip,str1) > findIntFromStr((char *)cit->pkt->pfx->comp[i]+skip,str1))){
                    oldVersionPfx = cit->pkt->pfx;
                    oldVersionCO = cit;
                    break;
                }
                else{ break;}
            }        
        }
    }
    return oldVersionCO;
}
#endif

#ifdef RECOMMENDED_CACHE_TIME
struct ccnl_content_s *
oldestCacheTimeExpiredContent(struct ccnl_relay_s *ccnl){
    struct ccnl_content_s *cit;
    struct ccnl_content_s *cacheTimeExpiredContent = NULL;
    double leastCacheTimeLeft = 10; // set initial value to anything greater than zero because of first time entry into the if condition below
    double cacheTimeLeft =0;
    for (cit = ccnl->contents; cit; cit = cit->next) {
        cacheTimeLeft = cit->recommended_cache_time - CCNL_NOW();
//        DEBUGMSG_CORE(DEBUG, " ICNIoT: RCT is %f, time now is %f cacheTimeLeft is %f\n",cit->recommended_cache_time, CCNL_NOW(), cacheTimeLeft);
        if ((cacheTimeLeft <= 0) && (leastCacheTimeLeft > cacheTimeLeft)){
           DEBUGMSG_CORE(DEBUG, " ICNIoT: RCT cacheTime expired\n");
           leastCacheTimeLeft = cacheTimeLeft;
           cacheTimeExpiredContent = cit;
        }
    }
    return cacheTimeExpiredContent;
}
#endif

struct ccnl_content_s*
ccnl_content_add2cache(struct ccnl_relay_s *ccnl, struct ccnl_content_s *c)
{
    struct ccnl_content_s *cit;

    for (cit = ccnl->contents; cit; cit = cit->next) {
        if (c == cit) {
            DEBUGMSG_CORE(DEBUG, "--- Already in cache ---\n");
            return NULL;
        }
    }
#ifdef USE_NACK
    if (ccnl_nfnprefix_contentIsNACK(c))
        return NULL;
#endif

    if (c->flags & CCNL_CONTENT_FLAGS_STATIC){
//        DEBUGMSG_CORE(INFO, " ICNIoT: going to add self published content to cache \n");
        DBL_LINKED_LIST_ADD(ccnl->contents, c);
        DEBUGMSG_CORE(INFO, " ICNIoT: added_content2cache without incrementing count:%d\n",ccnl->contentcnt);
        return c;
     }

   
// not self published content
    if (ccnl->max_cache_entries > 0 &&
        ccnl->contentcnt >= ccnl->max_cache_entries) { //Cache replacement strategy
        struct ccnl_content_s *c2;
        struct ccnl_content_s *c3 = NULL;
        int age = 0;
//        char* prefixBuf = NULL;



#ifdef UPDATE_TIME_SERIES
   	if(IsTimeSeriesContent(c->pkt->pfx)){
		DEBUGMSG_CORE(INFO, " ICNIoT: UTS-LRU The new received content is time series content\n");
        	c3 = findOlderVersion(ccnl, c->pkt->pfx);
        }
#endif

#ifdef RECOMMENDED_CACHE_TIME
      c3 = oldestCacheTimeExpiredContent(ccnl);
      if(c3)
          DEBUGMSG_CORE(INFO, " ICNIoT: RCT, Found a content object with expired RCT\n");        	      
#endif

	if (!c3){//if not time series CO OR if time series CO but older version of stream doesnt
                 //exist in cache. For both cases use LRU
		DEBUGMSG_CORE(INFO, " ICNIoT: using LRU\n");
        	for (c2 = ccnl->contents; c2; c2 = c2->next){
            		if (!(c2->flags & CCNL_CONTENT_FLAGS_STATIC) && ((age == 0) || c2->last_used < age)){
                		age = c2->last_used;
                		c3 = c2;
             		}
         	}
	}
//            prefixBuf = ccnl_prefix_to_path(c3->pkt->pfx);
//            DEBUGMSG_CORE(INFO, " ICNIoT: yes ! removed content\n");
//            free(prefixBuf);
            ccnl_content_remove(ccnl, c3);
    }
    if(ccnl->contentcnt < ccnl->max_cache_entries){
//        char* prefixBuf2 = NULL;
//        prefixBuf2 = ccnl_prefix_to_path(c->pkt->pfx);
//        DEBUGMSG_CORE(INFO, " ICNIoT: going to add %s content to cache\n",prefixBuf2);
//        free(prefixBuf2);
    	DBL_LINKED_LIST_ADD(ccnl->contents, c);
    	ccnl->contentcnt++;
    	DEBUGMSG_CORE(INFO, " ICNIoT: added_content2cache count:%d\n",ccnl->contentcnt);
    }
    return c;
}



// deliver new content c to all clients with (loosely) matching interest,
// but only one copy per face
// returns: number of forwards
int
ccnl_content_serve_pending(struct ccnl_relay_s *ccnl, struct ccnl_content_s *c, struct ccnl_face_s *from)
{
    struct ccnl_interest_s *i;
    struct ccnl_face_s *f;
    int cnt = 0;
    DEBUGMSG_CORE(TRACE, "ccnl_content_serve_pending\n");

    for (f = ccnl->faces; f; f = f->next){
                f->flags &= ~CCNL_FACE_FLAGS_SERVED; // reply on a face only once
    }
    for (i = ccnl->pit; i;) {
        struct ccnl_pendint_s *pi;
        if (!i->pkt->pfx)
            continue;

        switch (i->pkt->pfx->suite) {
#ifdef USE_SUITE_CCNB
        case CCNL_SUITE_CCNB:
            if (!ccnl_i_prefixof_c(i->pkt->pfx, i->pkt->s.ccnb.minsuffix,
                       i->pkt->s.ccnb.maxsuffix, c)) {
                // XX must also check i->ppkd
                i = i->next;
                continue;
            }
            break;
#endif
#ifdef USE_SUITE_CCNTLV
        case CCNL_SUITE_CCNTLV:
            if (ccnl_prefix_cmp(c->pkt->pfx, NULL, i->pkt->pfx, CMP_EXACT)) {
                // XX must also check keyid
                i = i->next;
                continue;
            }
            break;
#endif
#ifdef USE_SUITE_CISTLV
        case CCNL_SUITE_CISTLV:
            if (ccnl_prefix_cmp(c->pkt->pfx, NULL, i->pkt->pfx, CMP_EXACT)) {
                // XX must also check keyid
                i = i->next;
                continue;
            }
            break;
#endif
#ifdef USE_SUITE_IOTTLV
        case CCNL_SUITE_IOTTLV:
          if (ccnl_prefix_cmp(c->pkt->pfx, NULL, i->pkt->pfx, CMP_EXACT)) {
                // XX must also check keyid
                i = i->next;
                continue;
            }
            break;
#endif
#ifdef USE_SUITE_NDNTLV
        case CCNL_SUITE_NDNTLV:
            if (!ccnl_i_prefixof_c(i->pkt->pfx, i->pkt->s.ndntlv.minsuffix,
                       i->pkt->s.ndntlv.maxsuffix, c)) {
                // XX must also check i->ppkl,
                i = i->next;
                continue;
            }
            break;
#endif
        default:
            i = i->next;
            continue;
        }

        //Hook for add content to cache by callback:
        // only for self published content
        if(i && ! i->pending){
            DEBUGMSG_CORE(WARNING, "releasing interest 0x%p OK?\n", (void*)i);
            c->flags |= CCNL_CONTENT_FLAGS_STATIC;
            i = ccnl_interest_remove(ccnl, i);
            return 1;
        }

        // only hop received CO comes here NOT self published content
        // CONFORM: "Data MUST only be transmitted in response to
        // an Interest that matches the Data."
        if(!drop_this_pkt(ccnl, from)){
        	DEBUGMSG_CORE(INFO, " ICNIoT: CO_pkt NOT_dropped\n");
        for (pi = i->pending; pi; pi = pi->next) {
            if (pi->face->flags & CCNL_FACE_FLAGS_SERVED)
            continue;
            pi->face->flags |= CCNL_FACE_FLAGS_SERVED;
            if (pi->face->ifndx >= 0) {
		DEBUGMSG_CORE(INFO, " ICNIoT: outgoing_data\n");
                DEBUGMSG_CORE(VERBOSE, "    Serve to face: %d (pkt=%p)\n",
                         pi->face->faceid, (void*) c->pkt);
                ccnl_nfn_monitor(ccnl, pi->face, c->pkt->pfx,
                                 c->pkt->content, c->pkt->contlen);
                ccnl_face_enqueue(ccnl, pi->face, buf_dup(c->pkt->buf));
            } else {// upcall to deliver content to local client
                ccnl_app_RX(ccnl, c);
            }
            c->served_cnt++;
            cnt++;
        }
      }
      else{ DEBUGMSG_CORE(INFO, " ICNIoT: CO_pkt dropped\n");}

        i = ccnl_interest_remove(ccnl, i);
    }
    return cnt;
}

void
ccnl_do_ageing(void *ptr, void *dummy)
{
    struct ccnl_relay_s *relay = (struct ccnl_relay_s*) ptr;
    struct ccnl_content_s *c = relay->contents;
    struct ccnl_interest_s *i = relay->pit;
    struct ccnl_face_s *f = relay->faces;
    time_t t = CCNL_NOW();
    char *bufp = NULL;
    DEBUGMSG_CORE(INFO, " ICNIoT: ageing t=%d\n", (int)t);

    while (c) {
        if ((c->last_used + CCNL_CONTENT_TIMEOUT) <= t &&
                                !(c->flags & CCNL_CONTENT_FLAGS_STATIC)){
          DEBUGMSG_CORE(INFO, " ICNIoT: AGING: CONTENT REMOVE %p\n", (void*) c);
            c = ccnl_content_remove(relay, c);
        }
        else{
//akhila 29-10-2015
        // check if it is the n th time instant. If yes then save the content store 
             if ((((int)t)%CS_SAVE_PERIOD == 0) && !(c->flags & CCNL_CONTENT_FLAGS_STATIC)){
                 bufp = ccnl_prefix_to_path((c->pkt)->pfx);
                 DEBUGMSG_CORE(INFO, " ICNIoT: ContentStoreItem :%s\n",bufp);
                 ccnl_free(bufp);
             }
            c = c->next;
        }
    }
    if (((int)t)%CS_SAVE_PERIOD == 0){
    	DEBUGMSG_CORE(INFO, " ICNIoT: ContentStoreItem contentCount:%d\n",relay->contentcnt);
      }
    while (i) { // CONFORM: "Entries in the PIT MUST timeout rather
                // than being held indefinitely."
        if ((i->last_used + CCNL_INTEREST_TIMEOUT) <= t){ // if it has timed out either resend it or remove it based on MAX_RETRIES
                if(i->retries >= CCNL_MAX_INTEREST_RETRANSMIT){
            		DEBUGMSG_CORE(INFO, " ICNIoT: AGING: INTEREST REMOVE %p\n", (void*) i);
//            		DEBUGMSG_CORE(DEBUG, " timeout: remove interest 0x%p <%s>\n",(void*)i,ccnl_prefix_to_path(i->pkt->pfx));
            		i = ccnl_nfn_interest_remove(relay, i);
        	  }
        	else {
            		// CONFORM: "A node MUST retransmit Interest Messages
            		// periodically for pending PIT entries."
            		DEBUGMSG_CORE(INFO, " ICNIoT: retransmit %d \n", i->retries);
//                      ccnl_prefix_to_path(i->pkt->pfx));
#ifdef USE_NFN
            		if (i->flags & CCNL_PIT_COREPROPAGATES){
#endif
     		           DEBUGMSG_CORE(INFO, " ICNIoT: AGING: PROPAGATING INTEREST %p\n", (void*) i);
                	   ccnl_interest_propagate(relay, i);
#ifdef USE_NFN
                        }
#endif
            		i->retries++;
            		i = i->next;
        	}
         }
        else{ // The interest has not timed out yet, so leave it alone !
//		DEBUGMSG_CORE(INFO, " ICNIoT: AGING: DO NOTHING %p\n", (void*) i);
		i = i->next;
            } 
    }
//    DEBUGMSG_CORE(INFO, " ICNIoT: PITcount %d\n",relay->pitcnt);
    while (f) {
        if (!(f->flags & CCNL_FACE_FLAGS_STATIC) &&
                (f->last_used + CCNL_FACE_TIMEOUT) <= t){
            DEBUGMSG_CORE(TRACE, "AGING: FACE REMOVE %p\n", (void*) f);
            f = ccnl_face_remove(relay, f);
    }
        else
            f = f->next;
    }
}

int
ccnl_nonce_find_or_append(struct ccnl_relay_s *ccnl, struct ccnl_buf_s *nonce)
{
    struct ccnl_buf_s *n, *n2 = 0;
    int i;
    DEBUGMSG_CORE(TRACE, "ccnl_nonce_find_or_append\n");

    for (n = ccnl->nonces, i = 0; n; n = n->next, i++) {
        if (buf_equal(n, nonce))
            return -1;
        if (n->next)
            n2 = n;
    }
    n = ccnl_buf_new(nonce->data, nonce->datalen);
    if (n) {
        n->next = ccnl->nonces;
        ccnl->nonces = n;
        if (i >= CCNL_MAX_NONCES && n2) {
            ccnl_free(n2->next);
            n2->next = 0;
        }
    }
    return 0;
}

int
ccnl_nonce_isDup(struct ccnl_relay_s *relay, struct ccnl_pkt_s *pkt)
{
    switch (pkt->suite) {
#ifdef USE_SUITE_CCNB
    case CCNL_SUITE_CCNB:
        return pkt->s.ccnb.nonce &&
            ccnl_nonce_find_or_append(relay, pkt->s.ccnb.nonce);
#endif
#ifdef USE_SUITE_NDNTLV
    case CCNL_SUITE_NDNTLV:
        return pkt->s.ndntlv.nonce &&
            ccnl_nonce_find_or_append(relay, pkt->s.ndntlv.nonce);
#endif
    default:
        break;
    }
    return 0;
}

// ----------------------------------------------------------------------
// dispatching the different formats (and respective forwarding semantics):


#include "ccnl-pkt-switch.c"

#include "ccnl-pkt-ccnb.c"
#include "ccnl-pkt-ccntlv.c"
#include "ccnl-pkt-cistlv.c"
#include "ccnl-pkt-iottlv.c"
#include "ccnl-pkt-ndntlv.c"
#include "ccnl-pkt-localrpc.c" // must come after pkt-ndntlv.c

#include "ccnl-core-fwd.c"

struct ccnl_suite_s ccnl_core_suites[CCNL_SUITE_LAST];

void
ccnl_core_RX(struct ccnl_relay_s *relay, int ifndx, unsigned char *data,
             int datalen, struct sockaddr *sa, int addrlen)
{
    unsigned char *base = data;
    struct ccnl_face_s *from;
    int enc, suite = -1, skip;
    dispatchFct dispatch;

    (void) base; // silence compiler warning (if USE_DEBUG is not set)

    DEBUGMSG_CORE(DEBUG, "ccnl_core_RX ifndx=%d, %d bytes\n", ifndx, datalen);
    //    DEBUGMSG_ON(DEBUG, "ccnl_core_RX ifndx=%d, %d bytes\n", ifndx, datalen);

#ifdef USE_STATS
    if (ifndx >= 0)
        relay->ifs[ifndx].rx_cnt++;
#endif

    from = ccnl_get_face_or_create(relay, ifndx, sa, addrlen);
    if (!from) {
        DEBUGMSG_CORE(DEBUG, "  no face\n");
        return;
    } else {
        DEBUGMSG_CORE(DEBUG, "  face %d, peer=%s\n", from->faceid,
                    ccnl_addr2ascii(&from->peer));
    }

    // loop through all packets in the received frame (UDP, Ethernet etc)
    while (datalen > 0) {
        // work through explicit code switching
        while (!ccnl_switch_dehead(&data, &datalen, &enc))
            suite = ccnl_enc2suite(enc);
        if (suite == -1)
            suite = ccnl_pkt2suite(data, datalen, &skip);

        if (!ccnl_isSuite(suite)) {
            DEBUGMSG_CORE(WARNING, "?unknown packet format? ccnl_core_RX ifndx=%d, %d bytes starting with 0x%02x at offset %zd\n",
                     ifndx, datalen, *data, data - base);
            return;
        }
        //        dispatch = ccnl_core_RX_dispatch[suite];
        dispatch = ccnl_core_suites[suite].RX;
        if (!dispatch) {
            DEBUGMSG_CORE(ERROR, "Forwarder not initialized or dispatcher "
                     "for suite %s does not exist.\n", ccnl_suite2str(suite));
            return;
        }
        if (dispatch(relay, from, &data, &datalen) < 0)
            break;
        if (datalen > 0) {
            DEBUGMSG_CORE(WARNING, "ccnl_core_RX: %d bytes left\n", datalen);
        }
    }
}

// ----------------------------------------------------------------------

void
ccnl_core_init(void)
{
#ifdef USE_SUITE_CCNB
    ccnl_core_suites[CCNL_SUITE_CCNB].RX         = ccnl_ccnb_forwarder;
    ccnl_core_suites[CCNL_SUITE_CCNB].cMatch     = ccnl_ccnb_cMatch;
#endif
#ifdef USE_SUITE_CCNTLV
    ccnl_core_suites[CCNL_SUITE_CCNTLV].RX       = ccnl_ccntlv_forwarder;
    ccnl_core_suites[CCNL_SUITE_CCNTLV].cMatch   = ccnl_ccntlv_cMatch;
#endif
#ifdef USE_SUITE_CISTLV
    ccnl_core_suites[CCNL_SUITE_CISTLV].RX       = ccnl_cistlv_forwarder;
    ccnl_core_suites[CCNL_SUITE_CISTLV].cMatch   = ccnl_cistlv_cMatch;
#endif
#ifdef USE_SUITE_IOTTLV
    ccnl_core_suites[CCNL_SUITE_IOTTLV].RX       = ccnl_iottlv_forwarder;
    ccnl_core_suites[CCNL_SUITE_IOTTLV].cMatch   = ccnl_iottlv_cMatch;
#endif
#ifdef USE_SUITE_LOCALRPC
    ccnl_core_suites[CCNL_SUITE_LOCALRPC].RX     = ccnl_localrpc_exec;
    //    ccnl_core_suites[CCNL_SUITE_LOCALRPC].cMatch = ccnl_localrpc_cMatch;
#endif
#ifdef USE_SUITE_NDNTLV
    ccnl_core_suites[CCNL_SUITE_NDNTLV].RX       = ccnl_ndntlv_forwarder;
    ccnl_core_suites[CCNL_SUITE_NDNTLV].cMatch   = ccnl_ndntlv_cMatch;
#endif

#ifdef USE_NFN
    ZAM_init();
#endif
}

struct ccnl_buf_s *bufCleanUpList;

void
ccnl_core_addToCleanup(struct ccnl_buf_s *buf)
{
    buf->next = bufCleanUpList;
    bufCleanUpList = buf;
}

void
ccnl_core_cleanup(struct ccnl_relay_s *ccnl)
{
    int k;

    DEBUGMSG_CORE(TRACE, "ccnl_core_cleanup %p\n", (void *) ccnl);

    while (ccnl->pit)
        ccnl_interest_remove(ccnl, ccnl->pit);
    while (ccnl->faces)
        ccnl_face_remove(ccnl, ccnl->faces); // removes allmost all FWD entries
    while (ccnl->fib) {
        struct ccnl_forward_s *fwd = ccnl->fib->next;
        free_prefix(ccnl->fib->prefix);
        ccnl_free(ccnl->fib);
        ccnl->fib = fwd;
    }
    while (ccnl->contents)
        ccnl_content_remove(ccnl, ccnl->contents);
    while (ccnl->nonces) {
        struct ccnl_buf_s *tmp = ccnl->nonces->next;
        ccnl_free(ccnl->nonces);
        ccnl->nonces = tmp;
    }
    for (k = 0; k < ccnl->ifcount; k++)
        ccnl_interface_cleanup(ccnl->ifs + k);

    while (bufCleanUpList) {
        struct ccnl_buf_s *tmp = bufCleanUpList->next;
        ccnl_free(bufCleanUpList);
        bufCleanUpList = tmp;
    }

#ifdef USE_NFN
    ccnl_nfn_freeKrivine(ccnl);
#endif
}

#include "ccnl-core-util.c"

// eof
