/* Experimental RAW pre-capture: save C15/C30 pre-capture (history) frames as HE NEF beside the stock JPEG.
 *
 * Three call-site hooks, no trampolines, no writable globals:
 *   P1 0x40f6fe90  history drain  -> precapture_history_entry: bind a 128-byte record into the
 *                  frame's own E allocation tail, then the original submit 0x40f93098.
 *   P2 0x40ea915c  end of the Tdec stage -> precapture_tdec_release(R): for a recorded frame that
 *                  the card configuration selects, keep R+0x748 (E); otherwise the original
 *                  free and clear.
 *   P3 0x40ea367c  primary writer, after one file was written -> precapture_writer_file_done:
 *                  when that file is the retained frame's JPEG, assemble a NEF from the
 *                  JPEG's own header buffer (Exif, MakerNote, thumbnail, XMP), its MPF
 *                  preview streams, M and the untouched HE payload, write it beside the
 *                  JPEG, then free E. Finally the original header-buffer free.
 * A retained E whose JPEG never reaches P3 is freed by the original R cleanup 0x40ea44d0,
 * which frees any non-zero R+0x748. The CPU never reads the HE payload or the preview
 * streams; both go to WRITE by address.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long u64;
typedef long s64;

#define LOAD8(a) (*(volatile const u8 *)(u64)(a))
#define LOAD16(a) (*(volatile const u16 *)(u64)(a))
#define LOAD32(a) (*(volatile const u32 *)(u64)(a))
#define LOAD64(a) (*(volatile const u64 *)(u64)(a))
#define STORE64(a,v) (*(volatile u64 *)(u64)(a)=(v))

/* Original firmware interfaces (byte-audited by the build). */
#define SUBMIT ((u64 (*)(void *,u32))0x40f93098ul)
#define FREE_E ((void (*)(u64))0x4104df5cul)
#define FREE_HDR ((void (*)(u64))0x4104d600ul)
#define XLATE ((u64 (*)(u64))0x41186718ul)
#define OPEN ((int (*)(const char *,u32,u32))0x402daa4cul)
#define CREATE ((int (*)(const char *,u32))0x402dad04ul)
#define CLOSE ((int (*)(int))0x402daaacul)
#define READ ((int (*)(int,void *,u32,u32 *))0x402dab4cul)
#define WRITE ((int (*)(int,u64,u32,u32 *))0x402dabb8ul)
#define EXISTS ((int (*)(const char *))0x402db1acul)
#define RENAME ((int (*)(const char *,const char *))0x402dad58ul)
#define ALLOC ((void *(*)(u32,u32))0x40d2c408ul)
#define FREE ((void (*)(void *))0x40d2c448ul)
#define CLEAN ((void (*)(const void *,u32))0x40d2b8b8ul)
#define CLOCK ((void (*)(void *))0x40c7c778ul)
#define DCF_GET ((u64 (*)(u32))0x4085a8e0ul)
#define DCF_NAME ((u64 (*)(u64))0x4085bfe0ul)
#define DCF_PUT ((void (*)(u64))0x4085aa7cul)
/* Original globals, only read. */
#define G_MODE 0xa03bc6bc8ul       /* HSFC release mode: 6 = C15, 3 = C30 */
#define G_LIMIT 0xa03bc6bacul      /* pre-capture count of the menu setting */
#define G_DRAINED 0xa03bc5638ul    /* history frames drained at this full press */
#define G_WRITER_JOB 0xa03b891b8ul /* job of the primary writer 0x40ea340c */

#define PAYLOAD 0x01058600u
#define OLD_ALLOCATION 0x01082400u
#define NEW_ALLOCATION 0x01082600u
#define FX_DIMS 0x15902058u        /* 5520 << 16 | 8280 */
#define RAW_W 8280u
#define RAW_H 5520u
#define WORK_BYTES 0x40000u        /* one heap block per NEF, freed before return */
#define HDR_MAX 0x30000u           /* NEF header block */
#define TAB 0x30000u               /* entry table, ENT_MAX * 32 bytes */
#define NI 0x36000u                /* NEFInfo block, 1 KiB */
#define FOOT 0x38000u              /* 512-byte footer */
#define ZEROS 0x39000u             /* 4 KiB of zero for RAW alignment */
#define ENT_MAX 160u
#define CHUNK 0x100000u
#define DEFAULT_BUDGET 1500000u    /* cooperative per-file timeout; not an interruptible I/O deadline */
#define FRESH_US 120000000ul
#define F_ENABLE 1u
#define F_C30 2u
#define F_FULL 4u
#define F_FOOTER 8u
#define F_KNOWN 15u
#define Q_MARKED 1u
#define Q_RETAINED 2u
#define S_DONE 1u
#define S_BUDGET 3u
#define S_WRITE_FAIL 4u
#define S_RENAME_FAIL 5u

static const u8 qual_magic[16] = "Z8PREQUALv1";
static const u8 cfg_magic[16] = "Z8PRECFGv1";
static const u8 foot_magic[16] = "Z8PREFOOTv1";
static const u8 identity[8] = {'P','R','E','C','A','P','0','1'}; /* diagnostic format identity */
/* MakerNote 0x0051 for HE (internal compression 4, budget 2): the original leaf 0x406ea044
 * writes this from M+0x2ac=2; identical in every camera HE NEF examined. */
static const u8 he51[24] = {0x30,0x31,0x30,0x32,0x30,0x35,0x30,0x31,0,0,13,0,0,0,0,0,6,0,0,0,0,0,0,0};
static const u8 rat300[8] = {44,1,0,0,1,0,0,0};
static const u8 refbw[48] = {0,0,0,0,1,0,0,0, 255,0,0,0,1,0,0,0, 0,0,0,0,1,0,0,0,
                             255,0,0,0,1,0,0,0, 0,0,0,0,1,0,0,0, 255,0,0,0,1,0,0,0};
static const u8 tiffep[4] = {1,0,0,0};
static const u8 one8[1] = {1};
static const u8 cfa_dim[4] = {2,0,2,0};
static const u8 cfa_rggb[4] = {0,1,1,2};
static const u8 quality_raw[8] = {'R','A','W',' ',' ',' ',' ',0};
static const u8 xmp_ns[29] = "http://ns.adobe.com/xap/1.0/";
static const u8 nikon2[18] = {'N','i','k','o','n',0,2,0x11,0,0,'I','I',0x2a,0,8,0,0,0};
static const u8 nikon_ni[18] = {'N','i','k','o','n',0,1,3,0,0,'I','I',0x2a,0,8,0,0,0};
static const u8 type_size[13] = {0,1,1,2,4,8,1,1,2,4,8,4,8};
static const u16 skip0[] = {0x00fe,0x0103,0x014a,0x0201,0x0202,0x0214,0x02bc,0x8769,0x8825,0x9003,0x9216};
static const u16 skipx[] = {0x9000,0x9101,0x9102,0xa000,0xa001,0xa002,0xa003,0xa005,0x927c};
static const u16 skipm[] = {0x0004,0x0011,0x0016,0x0035,0x003d,0x0045,0x0051,0x0058,0x00a2};
static const u32 crc_table[256] = {
#include "crc32_table.inc"
};

static void copy(u8 *d,const u8 *s,u32 n) { while(n--) *d++=*s++; }
static void zero(u8 *d,u32 n) { while(n--) *d++=0; }
static int equal(const u8 *a,const u8 *b,u32 n) { u32 x=0; while(n--) x|=*a++^*b++; return x==0; }
static u32 get16(const u8 *p) { return (u32)p[0]|(u32)p[1]<<8; }
static u32 get32(const u8 *p) { return (u32)p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24; }
static u64 get64(const u8 *p) { return (u64)get32(p)|(u64)get32(p+4)<<32; }
static void set16(u8 *p,u32 v) { p[0]=(u8)v; p[1]=(u8)(v>>8); }
static void set32(u8 *p,u32 v) { for(u32 i=0;i<4;i++){p[i]=(u8)v;v>>=8;} }
static void set64(u8 *p,u64 v) { for(u32 i=0;i<8;i++){p[i]=(u8)v;v>>=8;} }
__attribute__((noinline)) static u32 crc32(const u8 *p,u32 n) {
    u32 c=0xffffffffu; while(n--) c=(c>>8)^crc_table[(c^*p++)&255]; return c^0xffffffffu;
}
static u32 crc16(const u8 *p,u32 n) {              /* CCITT-FALSE, as in NEFInfo blocks */
    u32 c=0xffff;
    while(n--){ c^=(u32)*p++<<8; for(u32 i=0;i<8;i++) c=(c&0x8000)?((c<<1)^0x1021)&0xffff:(c<<1)&0xffff; }
    return c;
}
static u64 now(void) { u64 t; CLOCK(&t); return t; }

/* ---------------- frame record in the E allocation tail ---------------- */
/* E is a resource descriptor: E+8 -> {data_base, data_bytes}; E+0x30 type/format/dims,
 * E+0x40 payload. The 512 bytes past OLD_ALLOCATION exist only because the build enlarges
 * the mode 3/6 request; no original code addresses them. */
static u8 *record(u64 e) {
    u64 block=LOAD64(e+8); if(!block) return 0;
    u64 base=LOAD64(block),bytes=LOAD32(block+8);
    if(!base || bytes<NEW_ALLOCATION || base+bytes<base) return 0;
    u64 q=(base+OLD_ALLOCATION+63)&~63ul;
    if(q<base || q+128>base+bytes) return 0;
    return (u8 *)q;
}
static int e_shape(u64 e) {
    if(!e || LOAD32(e+0x30)!=3 || LOAD32(e+0x34)!=5 || LOAD32(e+0x38)!=FX_DIMS) return 0;
    u64 d=LOAD64(e+0x40); return d && !(d&511) && d+PAYLOAD>d;
}
static void seal(u8 *q) { set32(q+0x78,crc32(q,0x78)); CLEAN(q,128); }
static void unbind(u8 *q) { zero(q,16); CLEAN(q,128); }
/* Valid record of this exact HSFC R/E/M in the given state. */
static u8 *bound(u64 r,u64 e,u32 state) {
    u64 m=LOAD64(r+0x790); u8 *q;
    if(!m || LOAD32(m)!=3 || !e_shape(e) || !(q=record(e))) return 0;
    if(!equal(q,qual_magic,16) || get32(q+0x10)!=1 || get32(q+0x14)!=state) return 0;
    if(get64(q+0x28)!=r || get64(q+0x30)!=e || get64(q+0x38)!=m || get64(q+0x40)!=LOAD64(e+0x40)) return 0;
    if(get32(q+0x78)!=crc32(q,0x78)) return 0;
    return q;
}

__attribute__((noinline)) static void mark_history(void *rec) {
    u64 r=(u64)rec,m,e; u8 *q; u32 mode,seq,total;
    if(!r) return;
    m=LOAD64(r+0x790); e=LOAD64(r+0x748);
    if(!m || !e || LOAD32(m)!=3) return;
    mode=LOAD32(G_MODE); if(mode!=6 && mode!=3) return;
    seq=LOAD32(m+0x120); total=LOAD32(G_DRAINED);
    if(!seq || seq>total || total>30) return;
    if(!e_shape(e) || !(q=record(e))) return;
    zero(q,128); copy(q,qual_magic,16); set32(q+0x10,1); set32(q+0x14,Q_MARKED);
    set32(q+0x18,seq); set32(q+0x1c,total); set32(q+0x20,mode); set32(q+0x24,LOAD32(G_LIMIT));
    set64(q+0x28,r); set64(q+0x30,e); set64(q+0x38,m); set64(q+0x40,LOAD64(e+0x40));
    set32(q+0x48,LOAD32(e)); set32(q+0x4c,NEW_ALLOCATION); CLOCK(q+0x50);
    seal(q);
}
__attribute__((used,section(".text.entry"))) u64 precapture_history_entry(void *rec,u32 keep) {
    mark_history(rec);               /* RAM only, inside the original drain lock */
    return SUBMIT(rec,keep);
}

/* ---------------- card configuration and sticky stop ---------------- */
static int read_cfg(char drive,u8 *out) {
    char path[16]="A:\\Z8PRE.CFG"; u32 count=0; int fd,rc,cl;
    path[0]=drive;
    fd=OPEN(path,0,0x20); if(fd<0) return 0;
    rc=READ(fd,out,65,&count); cl=CLOSE(fd);
    if(rc!=0 || cl!=0 || count!=64 || !equal(out,cfg_magic,16)) return 0;
    u32 flags=get32(out+0x10),pre=get32(out+0x14),budget=get32(out+0x18);
    if((flags&~F_KNOWN) || !(flags&F_ENABLE) || pre<1 || pre>30) return 0;
    if(budget && (budget<200000 || budget>5000000)) return 0;
    for(u32 i=0x20;i<0x3c;i++) if(out[i]) return 0;
    return get32(out+0x3c)==crc32(out,60);
}
static int stopped(char drive) { char p[20]="A:\\Z8PRESTP.BIN"; p[0]=drive; return EXISTS(p)>=0; }
__attribute__((noinline)) static void stop_file(char drive,u32 status,u32 shot) {
    char p[20]="A:\\Z8PRESTP.BIN"; u8 raw[64] __attribute__((aligned(64))); u32 n; int fd;
    p[0]=drive; if(EXISTS(p)>=0) return;
    zero(raw,64); copy(raw,(const u8 *)"Z8PRESTOP",9); set32(raw+16,status); set32(raw+20,shot);
    set64(raw+24,now()); CLEAN(raw,64);
    fd=CREATE(p,0x20); if(fd<0) return;
    WRITE(fd,(u64)raw,32,&n); CLOSE(fd);        /* never retried or deleted */
}

/* P2. Original: ldr x0,[x23,#0x748]; bl 0x4104df5c; str xzr,[x23,#0x748]. */
__attribute__((used)) void precapture_tdec_release(u64 r) {
    u64 e=LOAD64(r+0x748); u8 *q=e?bound(r,e,Q_MARKED):0;
    if(q) {
        u8 ca[65] __attribute__((aligned(8))),cb[65] __attribute__((aligned(8)));
        u64 t=now(),m=LOAD64(r+0x790);
        int a=read_cfg('A',ca),b=read_cfg('B',cb);
        if(a!=b && t-get64(q+0x50)<FRESH_US) {
            char drive=a?'A':'B'; const u8 *c=a?ca:cb;
            u32 flags=get32(c+0x10),pre=get32(c+0x14),budget=get32(c+0x18);
            u32 seq=get32(q+0x18),total=get32(q+0x1c),mode=get32(q+0x20);
            if(!budget) budget=DEFAULT_BUDGET;
            if((mode==6 || (mode==3 && (flags&F_C30))) && seq+pre>total && !stopped(drive)) {
                set32(q+0x14,Q_RETAINED); set64(q+0x58,t); set32(q+0x60,flags); set32(q+0x64,pre);
                set32(q+0x68,budget); set32(q+0x6c,(u32)drive); set32(q+0x70,LOAD32(m+0x2508));
                set32(q+0x74,get32(c+0x1c));
                seal(q);
                return;                      /* R+0x748 kept for P3 or the R cleanup */
            }
        }
        unbind(q);
    }
    FREE_E(e);
    STORE64(r+0x748,0);
}

/* ---------------- TIFF reading and writing ---------------- */
typedef struct { const u8 *b; u32 n; } src_t;      /* little-endian TIFF, offsets from b */
typedef struct {
    u16 tag,type; u32 count;
    const u8 *data; u32 bytes;
    u8 slot,dslot,eslot,pad;   /* record value / data / entry position into patch[] */
} ent_t;
typedef struct { u8 *o; u32 pos,cap,bad; u32 patch[16]; } out_t;
enum { P_SUB=1,P_THUMB,P_EXIF,P_GPS,P_JFR,P_OTHER,P_STRIP,P_MNENT,P_MNPV,P_PVSTART };

static u32 ifd_count(const src_t *s,u32 off) {
    if(off<8 || off>s->n-2) return 0;
    u32 n=get16(s->b+off);
    if(!n || n>200 || 2+12*n+4>s->n-off) return 0;
    return n;
}
static const u8 *ent_data(const src_t *s,u32 off,u32 i,u32 *bytes) {
    const u8 *e=s->b+off+2+12*i; u32 t=get16(e+2),c=get32(e+4),sz;
    if(t==0 || t>12 || c>0x100000) return 0;
    sz=type_size[t]*c; *bytes=sz;
    if(sz<=4) return e+8;
    u32 v=get32(e+8); if(v>s->n || sz>s->n-v) return 0;
    return s->b+v;
}
static const u8 *find(const src_t *s,u32 off,u32 tag,u32 type,u32 count) {
    u32 n=ifd_count(s,off),bytes;
    for(u32 i=0;i<n;i++) {
        const u8 *e=s->b+off+2+12*i;
        if(get16(e)!=tag) continue;
        if(get16(e+2)!=type || get32(e+4)!=count) return 0;
        return ent_data(s,off,i,&bytes);
    }
    return 0;
}
static void put(out_t *w,const u8 *p,u32 n) {
    if(w->bad || n>w->cap-w->pos) { w->bad=1; return; }
    if(p) copy(w->o+w->pos,p,n); else zero(w->o+w->pos,n);
    w->pos+=n;
}
static void pad2(out_t *w) { if(w->pos&1) put(w,0,1); }
static ent_t *add(ent_t *t,u32 *n,u32 tag,u32 type,u32 count,const u8 *data) {
    if(*n>=ENT_MAX) return 0;
    ent_t *e=t+(*n)++; zero((u8 *)e,sizeof(*e));
    e->tag=(u16)tag; e->type=(u16)type; e->count=count; e->data=data; e->bytes=type_size[type]*count;
    return e;
}
static int skipped(u32 tag,const u16 *skip,u32 ns) { for(u32 j=0;j<ns;j++) if(skip[j]==tag) return 1; return 0; }
static int copy_entries(const src_t *s,u32 off,ent_t *t,u32 *n,const u16 *skip,u32 ns) {
    u32 k=ifd_count(s,off),bytes; if(!k) return 0;
    for(u32 i=0;i<k;i++) {
        const u8 *e=s->b+off+2+12*i; u32 tag=get16(e);
        if(skipped(tag,skip,ns)) continue;
        const u8 *d=ent_data(s,off,i,&bytes); if(!d) return 0;
        if(!add(t,n,tag,get16(e+2),get32(e+4),d)) return 0;
    }
    return 1;
}
static void sort(ent_t *t,u32 n) {
    for(u32 i=1;i<n;i++) for(u32 j=i;j>0 && t[j-1].tag>t[j].tag;j--) {
        ent_t x; copy((u8 *)&x,(u8 *)&t[j],sizeof(x)); copy((u8 *)&t[j],(u8 *)&t[j-1],sizeof(x));
        copy((u8 *)&t[j-1],(u8 *)&x,sizeof(x));
    }
}
/* IFD then its out-of-line data; stored offsets are (position - rel). Returns position. */
static u32 emit(out_t *w,ent_t *t,u32 n,u32 rel) {
    sort(t,n);
    for(u32 i=1;i<n;i++) if(t[i].tag==t[i-1].tag) w->bad=1;
    pad2(w); if(w->bad) return 0;
    u32 at=w->pos; u8 b[2]; set16(b,n); put(w,b,2);
    u32 vals=w->pos; put(w,0,12*n+4);
    if(w->bad) return 0;
    for(u32 i=0;i<n;i++) {
        u8 *e=w->o+vals+12*i;
        set16(e,t[i].tag); set16(e+2,t[i].type); set32(e+4,t[i].count);
        if(t[i].eslot) w->patch[t[i].eslot]=vals+12*i;
        if(t[i].slot) w->patch[t[i].slot]=vals+12*i+8;
        if(t[i].bytes<=4) { if(t[i].data) copy(e+8,t[i].data,t[i].bytes); continue; }
        pad2(w); if(w->bad) return 0;
        set32(w->o+vals+12*i+8,w->pos-rel);
        if(t[i].dslot) w->patch[t[i].dslot]=w->pos;
        put(w,t[i].data,t[i].bytes);
    }
    return w->bad?0:at;
}
static void patch32(out_t *w,u32 slot,u32 v) { if(!w->patch[slot]) { w->bad=1; return; } set32(w->o+w->patch[slot],v); }

typedef struct { u64 addr; u32 size; } stream_t;
static int stream(u64 d,stream_t *s) {
    if(!d) return 0;
    s->addr=LOAD64(d+8); s->size=LOAD32(d+0x10);
    return s->addr && s->size>=4 && s->size<0x2000000 && s->addr+s->size>s->addr;
}
typedef struct {
    u32 hdr_end,vga_at,fhd_at,main_at,raw_at,end_at,mn_at,thumb_bytes;
    stream_t main,vga,fhd;
} lay_t;
static u8 *nb(u8 *p,const char *v,const u8 *body,u32 n,u32 zeros) {   /* "0100"+body[+0000]+CRC16 */
    copy(p,(const u8 *)v,4); copy(p+4,body,n); zero(p+4+n,zeros);
    set16(p+4+n+zeros,crc16(p,4+n+zeros)); return p;
}

/* Header block: TIFF, IFD0, SubIFDs, GPS, Exif, thumbnail, MakerNote (+PreviewIFD); the
 * VGA preview stream follows directly as the MakerNote's last bytes.
 * h is the CPU view of the stock JPEG header buffer: SOI, APP1 Exif, APP1 XMP, APP2 MPF. */
static int build(out_t *w,const u8 *h,u32 hl,const u32 *hlen,u64 m,lay_t *L,u32 flags,u8 *wk) {
    ent_t *t=(ent_t *)(wk+TAB); u32 n;
    if(hl<0x400 || get32(h)!=0xe1ffd8ffu || LOAD32(m+0x2bc)!=0) return 0;   /* M+0x2bc=0: RGGB */
    u32 l1=(u32)h[4]<<8|h[5];
    if(l1<16 || 4+l1>hl || !equal(h+6,(const u8 *)"Exif\0\0",6)) return 0;
    src_t T={h+12,l1-8};
    if(get32(T.b)!=0x002a4949u) return 0;
    const u8 *xmp=0; u32 xmpn=0,at=4+l1,mpf=0;
    while(at+4<=hl && h[at]==0xff && (h[at+1]==0xe1 || h[at+1]==0xe2)) {
        u32 len=(u32)h[at+2]<<8|h[at+3]; if(len<2 || len>hl-at-2) return 0;
        if(h[at+1]==0xe1 && len>2+29 && equal(h+at+4,xmp_ns,29)) { xmp=h+at+4+29; xmpn=len-2-29; }
        if(h[at+1]==0xe2 && len>16 && equal(h+at+4,(const u8 *)"MPF\0",4)) mpf=at+8;
        at+=2+len;
    }
    if(!mpf || at!=hl) return 0;
    /* MPF index must describe exactly this header plus the three descriptor streams. */
    { src_t P={h+mpf,hl-mpf};
      if(get32(P.b)!=0x002a4949u) return 0;
      const u8 *mp=find(&P,get32(P.b+4),0xb002,7,48);
      if(!mp) return 0;
      if(get32(mp+4)!=hlen[0]+L->main.size-2 || get32(mp+20)!=hlen[1]+L->vga.size-2 ||
         get32(mp+36)!=hlen[2]+L->fhd.size-2) return 0; }
    u32 i0=get32(T.b+4),n0=ifd_count(&T,i0); if(!n0) return 0;
    u32 i1=get32(T.b+i0+2+12*n0);
    const u8 *x0=find(&T,i0,0x8769,4,1); if(!x0) return 0;
    u32 ix=get32(x0); if(!ifd_count(&T,ix)) return 0;
    const u8 *g0=find(&T,i0,0x8825,4,1); u32 ig=g0?get32(g0):0;
    if(g0 && !ifd_count(&T,ig)) return 0;
    const u8 *tho=find(&T,i1,0x0201,4,1),*thl=find(&T,i1,0x0202,4,1);
    if(!tho || !thl) return 0;
    u32 thumb=get32(tho),thn=get32(thl);
    if(thn<4 || thumb>T.n || thn>T.n-thumb || get16(T.b+thumb)!=0xd8ff || get16(T.b+thumb+thn-2)!=0xd9ff) return 0;
    const u8 *dto=find(&T,ix,0x9003,2,20);
    /* MakerNote */
    u32 mnc=0,mnoff=0,nx=ifd_count(&T,ix);
    for(u32 i=0;i<nx;i++) if(get16(T.b+ix+2+12*i)==0x927c) { mnc=get32(T.b+ix+2+12*i+4); mnoff=get32(T.b+ix+2+12*i+8); }
    if(mnc<64 || mnoff>T.n || mnc>T.n-mnoff || !equal(T.b+mnoff,nikon2,14)) return 0;
    src_t MN={T.b+mnoff+10,mnc-10}; u32 im=get32(MN.b+4); if(!ifd_count(&MN,im)) return 0;
    const u8 *wb=find(&MN,im,0x000c,5,4),*v54=find(&MN,im,0x0054,7,20),*bnd=find(&MN,im,0x0016,3,4);
    if(!wb || !v54 || !bnd) return 0;
    u32 bx=get16(bnd),by=get16(bnd+2),iw=get16(bnd+4)-bx,ih=get16(bnd+6)-by;
    if(get16(bnd+4)<=bx || get16(bnd+6)<=by || iw>RAW_W || ih>RAW_H || (RAW_W-iw)&1 || (RAW_H-ih)&1) return 0;
    u8 *v=wk+NI;                    /* small computed values */
    for(u32 k=0;k<4;k++) set16(v+k*2,LOAD16(m+0x2b4+2*k));                 /* black   v+0  */
    set16(v+8,(RAW_W-iw)/2); set16(v+10,(RAW_H-ih)/2); set16(v+12,iw); set16(v+14,ih); /* crop v+8 */
    copy(v+16,(const u8 *)"0100",4); set32(v+20,PAYLOAD); set32(v+24,1);  /* 0x0058  v+16 */
    u32 jfr=(flags&F_FULL)?L->main.size:L->fhd.size;
    set32(v+28,RAW_W); set32(v+32,RAW_H); set32(v+36,PAYLOAD); set32(v+40,jfr);
    set32(v+44,thn); set32(v+48,L->fhd.size); set32(v+52,L->vga.size); set16(v+56,14); set16(v+58,34713);
    set16(v+60,32803); set16(v+62,1); set16(v+64,2); set16(v+66,6); set32(v+68,1); set32(v+72,0);
    /* NEFInfo (RAW IFD 0xc7d5): blocks 8,9,a,b,d,f; CRC16 per block. Adobe needs 9 and d. */
    u8 *nib=v+128; u8 *b8=nb(nib,"0100",v54+4,16,2),*b9=nib+32,*ba=nib+80,*bb=nib+96,*bd=nib+112,*bf=nib+128;
    copy(b9,wb,32); zero(b9+32,2); set16(b9+34,crc16(b9,34));
    nb(ba,"0100",v,8,0); nb(bb,"0100",v+8,8,0); nb(bd,"0100",(const u8 *)"\x0d\0",2,0); nb(bf,"0100",v+20,8,0);
    out_t ni; zero((u8 *)&ni,sizeof(ni)); ni.o=v+512; ni.cap=512; put(&ni,nikon_ni,18); n=0;
    add(t,&n,0x8,7,24,b8); add(t,&n,0x9,7,36,b9); add(t,&n,0xa,7,14,ba);
    add(t,&n,0xb,7,14,bb); add(t,&n,0xd,7,8,bd); add(t,&n,0xf,7,14,bf);
    if(emit(&ni,t,n,10)!=18 || ni.bad) return 0;
    const u8 *nefinfo=v+512; u32 nin=ni.pos;
    /* ---- emission ---- */
    u8 hd[8]={'I','I',0x2a,0,8,0,0,0}; put(w,hd,8);
    n=0; if(!copy_entries(&T,i0,t,&n,skip0,sizeof(skip0)/2)) return 0;
    add(t,&n,0x00fe,4,1,v+68); add(t,&n,0x0103,3,1,v+66);
    ent_t *e=add(t,&n,0x014a,4,(flags&F_FULL)?3:2,0); if(!e) return 0; e->dslot=P_SUB;
    e=add(t,&n,0x0201,4,1,0); if(!e) return 0; e->slot=P_THUMB;
    add(t,&n,0x0202,4,1,v+44); add(t,&n,0x0214,5,6,refbw);
    if(xmp) add(t,&n,0x02bc,1,xmpn,xmp);
    e=add(t,&n,0x8769,4,1,0); if(!e) return 0; e->slot=P_EXIF;
    if(g0) { e=add(t,&n,0x8825,4,1,0); if(!e) return 0; e->slot=P_GPS; }
    if(dto) add(t,&n,0x9003,2,20,dto);
    if(!add(t,&n,0x9216,1,4,tiffep)) return 0;
    if(emit(w,t,n,0)!=8) return 0;
    u32 sub[3];
    n=0; add(t,&n,0x00fe,4,1,v+68); add(t,&n,0x0103,3,1,v+66); add(t,&n,0x011a,5,1,rat300);
    add(t,&n,0x011b,5,1,rat300); add(t,&n,0x0128,3,1,v+64);
    e=add(t,&n,0x0201,4,1,0); e->slot=P_JFR; add(t,&n,0x0202,4,1,v+40); add(t,&n,0x0213,3,1,v+64);
    sub[0]=emit(w,t,n,0);
    n=0; add(t,&n,0x00fe,4,1,v+72); add(t,&n,0x0100,4,1,v+28); add(t,&n,0x0101,4,1,v+32);
    add(t,&n,0x0102,3,1,v+56); add(t,&n,0x0103,3,1,v+58); add(t,&n,0x0106,3,1,v+60);
    e=add(t,&n,0x0111,4,1,0); e->slot=P_STRIP; add(t,&n,0x0115,3,1,v+62); add(t,&n,0x0116,4,1,v+32);
    add(t,&n,0x0117,4,1,v+36); add(t,&n,0x011a,5,1,rat300); add(t,&n,0x011b,5,1,rat300);
    add(t,&n,0x011c,3,1,v+62); add(t,&n,0x0128,3,1,v+64); add(t,&n,0x828d,3,2,cfa_dim);
    add(t,&n,0x828e,1,4,cfa_rggb); add(t,&n,0x9217,3,1,v+64); add(t,&n,0xc7d5,7,nin,nefinfo);
    add(t,&n,0xc7d6,1,1,one8);
    sub[1]=emit(w,t,n,0);
    if(flags&F_FULL) {
        n=0; add(t,&n,0x00fe,4,1,v+68); add(t,&n,0x0103,3,1,v+66); add(t,&n,0x011a,5,1,rat300);
        add(t,&n,0x011b,5,1,rat300); add(t,&n,0x0128,3,1,v+64);
        e=add(t,&n,0x0201,4,1,0); e->slot=P_OTHER; add(t,&n,0x0202,4,1,v+48); add(t,&n,0x0213,3,1,v+64);
        sub[2]=emit(w,t,n,0);
    }
    u32 gat=0;
    if(g0) { n=0; if(!copy_entries(&T,ig,t,&n,0,0)) return 0; gat=emit(w,t,n,0); }
    n=0; if(!copy_entries(&T,ix,t,&n,skipx,sizeof(skipx)/2)) return 0;
    e=add(t,&n,0x927c,7,4,0); if(!e) return 0; e->eslot=P_MNENT;
    u32 xat=emit(w,t,n,0);
    pad2(w); u32 tat=w->pos; put(w,T.b+thumb,thn);
    /* MakerNote rebuilt with its IFD at offset 8; every value relocated into it. */
    pad2(w); L->mn_at=w->pos; u32 mb=w->pos+10; put(w,nikon2,18);
    n=0; if(!copy_entries(&MN,im,t,&n,skipm,sizeof(skipm)/2)) return 0;
    add(t,&n,0x0004,2,8,quality_raw);
    e=add(t,&n,0x0011,4,1,0); if(!e) return 0; e->slot=P_MNPV;
    add(t,&n,0x003d,3,4,v); add(t,&n,0x0045,3,4,v+8); add(t,&n,0x0051,7,24,he51);
    if(!add(t,&n,0x0058,7,12,v+16)) return 0;
    if(emit(w,t,n,mb)!=mb+8) return 0;
    n=0; add(t,&n,0x0103,3,1,v+66); add(t,&n,0x011a,5,1,rat300); add(t,&n,0x011b,5,1,rat300);
    add(t,&n,0x0128,3,1,v+64); e=add(t,&n,0x0201,4,1,0); e->slot=P_PVSTART;
    add(t,&n,0x0202,4,1,v+52); add(t,&n,0x0213,3,1,v+64);
    u32 pat=emit(w,t,n,mb);
    pad2(w); if(w->bad || !sub[0] || !sub[1] || !xat || !pat) return 0;
    /* ---- layout of the streams after the header block ---- */
    L->hdr_end=w->pos; L->vga_at=w->pos; L->fhd_at=L->vga_at+L->vga.size;
    L->main_at=L->fhd_at+L->fhd.size;
    u32 end=L->main_at+((flags&F_FULL)?L->main.size:0);
    L->raw_at=(end+4095)&~4095u; L->end_at=L->raw_at+PAYLOAD; L->thumb_bytes=thn;
    set32(w->o+w->patch[P_SUB],sub[0]); set32(w->o+w->patch[P_SUB]+4,sub[1]);
    if(flags&F_FULL) { set32(w->o+w->patch[P_SUB]+8,sub[2]); patch32(w,P_OTHER,L->fhd_at); }
    patch32(w,P_THUMB,tat); patch32(w,P_EXIF,xat); if(g0) patch32(w,P_GPS,gat);
    patch32(w,P_JFR,(flags&F_FULL)?L->main_at:L->fhd_at); patch32(w,P_STRIP,L->raw_at);
    patch32(w,P_MNPV,pat-mb); patch32(w,P_PVSTART,L->vga_at-mb);
    if(!w->patch[P_MNENT]) return 0;
    set32(w->o+w->patch[P_MNENT]+4,L->vga_at+L->vga.size-L->mn_at);
    set32(w->o+w->patch[P_MNENT]+8,L->mn_at);
    return !w->bad;
}

/* ---------------- P3 NEF write ---------------- */
static int write_all(int fd,u64 p,u32 n) { u32 c=0; return WRITE(fd,p,n,&c)==0 && c==n; }
static int jpg_name(u32 id,char *fin,char *tmp) {
    u64 fo=DCF_GET(id); if(!fo) return 0;
    u64 nm=DCF_NAME(fo); u32 len=nm?LOAD32(nm+0x20):0; int ok=0;
    if(nm && len>=12 && len<60) {
        for(u32 i=0;i<len;i++) fin[i]=(char)LOAD8(nm+i);
        fin[len]=0; ok=1;
        for(u32 i=0;i<len;i++) if(!fin[i]) ok=0;
        char *x=fin+len-4;
        if(x[0]!='.' || (x[1]|32)!='j' || (x[2]|32)!='p' || (x[3]|32)!='g') ok=0;
        if(ok) { x[1]='N'; x[2]='E'; x[3]='F'; copy((u8 *)tmp,(const u8 *)fin,len+1); tmp[len-1]='_'; }
    }
    DCF_PUT(fo);
    return ok;
}
__attribute__((noinline)) static void nef_write(u64 r,u64 m,u64 e,u64 J,u8 *q) {
    u32 flags=get32(q+0x60),budget=get32(q+0x68); char drive=(char)get32(q+0x6c);
    u64 t0=now(),hp,lp=LOAD64(J+0x18),da=LOAD64(J+0x10); u32 hlen[3],hcap,hl;
    lay_t L; char fin[64],tmp[64];
    zero((u8 *)fin,sizeof(fin)); zero((u8 *)tmp,sizeof(tmp));
    if(!lp || !da) return;
    hp=LOAD64(lp); hcap=LOAD32(lp+8); hl=LOAD32(lp+0xc); hlen[0]=hl; hlen[1]=LOAD32(lp+0x1c); hlen[2]=LOAD32(lp+0x2c);
    if(!hp || hl<0x400 || hl>hcap || hl>0x40000) return;
    if(!stream(LOAD64(da),&L.main) || !stream(LOAD64(da+8),&L.vga) || !stream(LOAD64(da+16),&L.fhd)) return;
    if(stopped(drive)) return;            /* an earlier failure in this or a previous burst */
    if(!jpg_name(LOAD32(J),fin,tmp) || EXISTS(fin)>=0 || EXISTS(tmp)>=0) return;
    u8 *raw=(u8 *)ALLOC(WORK_BYTES+63,0); if(!raw) return;
    u8 *wk=(u8 *)(((u64)raw+63)&~63ul);
    zero(wk+TAB,WORK_BYTES-TAB);
    out_t w; zero((u8 *)&w,sizeof(w)); w.o=wk; w.cap=HDR_MAX;
    if(!build(&w,(const u8 *)XLATE(hp),hl,hlen,m,&L,flags,wk) || L.end_at<L.raw_at) { FREE(raw); return; }
    u64 t1=now(),t2=0,t3=0,t4=0,t5=0; u32 status=S_DONE,written=0,chunks=0,times[17];
    zero((u8 *)times,sizeof(times));
#ifndef NEG_NO_CLEAN                 /* negative-control builds only */
    CLEAN(wk,w.pos);
#endif
    CLEAN(wk+ZEROS,4096);
    int fd=CREATE(tmp,0x20);
    if(fd<0) { FREE(raw); stop_file(drive,S_WRITE_FAIL,get32(q+0x70)); return; }
    t2=now();
    if(!write_all(fd,(u64)wk,w.pos) || !write_all(fd,L.vga.addr,L.vga.size) || !write_all(fd,L.fhd.addr,L.fhd.size) ||
       ((flags&F_FULL) && !write_all(fd,L.main.addr,L.main.size)) ||
       (L.raw_at>L.main_at+((flags&F_FULL)?L.main.size:0) && !write_all(fd,(u64)(wk+ZEROS),L.raw_at-L.main_at-((flags&F_FULL)?L.main.size:0))))
        status=S_WRITE_FAIL;
    t3=now();
    if(status==S_DONE && t3-t0>=budget) status=S_BUDGET;
    u64 data=LOAD64(e+0x40);
#ifdef NEG_READ_PAYLOAD               /* negative-control builds only */
    if(LOAD32(data+0x1000)==0x12345678u) status=S_WRITE_FAIL;
#endif
    while(status==S_DONE && written<PAYLOAD) {
        u32 part=PAYLOAD-written; if(part>CHUNK) part=CHUNK;
        u32 c=0; int rc=WRITE(fd,data+written,part,&c);
        written+=c<=part?c:0;
        u64 after=now(); if(chunks<17) times[chunks]=(u32)(after-t0); chunks++;
        if(rc!=0 || c!=part) status=S_WRITE_FAIL;
        else if(after-t0>=budget && written<PAYLOAD) status=S_BUDGET;
    }
    t4=now();
    if(flags&F_FOOTER) {
        u8 *f=wk+FOOT; zero(f,512); copy(f,foot_magic,16);
        set32(f+0x10,1); set32(f+0x14,status); set32(f+0x18,written); set32(f+0x1c,chunks);
        set64(f+0x20,t0); set64(f+0x28,t1); set64(f+0x30,t2); set64(f+0x38,t3); set64(f+0x40,t4);
        set32(f+0x58,w.pos); set32(f+0x5c,L.vga.size); set32(f+0x60,L.fhd.size); set32(f+0x64,(flags&F_FULL)?L.main.size:0);
        set32(f+0x68,L.raw_at); set32(f+0x6c,L.end_at); set32(f+0x70,LOAD32(m+0x2508)); set32(f+0x74,LOAD32(m+0x120));
        set32(f+0x78,LOAD32(J)); set32(f+0x7c,hl);
        set64(f+0x80,r); set64(f+0x88,e); set64(f+0x90,m); set64(f+0x98,data); set64(f+0xa0,J);
        set64(f+0xa8,L.vga.addr); set64(f+0xb0,L.fhd.addr); set64(f+0xb8,L.main.addr);
        for(u32 i=0;i<17;i++) set32(f+0xc0+4*i,times[i]);
        copy(f+0x108,identity,8); copy(f+0x110,(const u8 *)fin,48);
        copy(f+0x140,q,128);
        t5=now(); set64(f+0x48,t5);
        set32(f+0x1fc,crc32(f,0x1fc)); CLEAN(f,512);
        if(!write_all(fd,(u64)f,512) && status==S_DONE) status=S_WRITE_FAIL;
    }
    if(CLOSE(fd)!=0 && status==S_DONE) status=S_WRITE_FAIL;
    if(status==S_DONE && RENAME(tmp,fin)!=0) status=S_RENAME_FAIL;
    FREE(raw);
    if(status!=S_DONE) stop_file(drive,status,get32(q+0x70));
}

/* P3. Original: bl 0x4104d600 (header resource of the file just written). */
__attribute__((used)) void precapture_writer_file_done(u64 hres) {
    u64 job=LOAD64(G_WRITER_JOB);
    if(job && !LOAD8(job+4)) {
        u64 r=LOAD64(job+0x18); u32 idx=LOAD32(job+0xbc)-1;
        u64 m=r?LOAD64(r+0x790):0, e=r?LOAD64(r+0x748):0;
        if(m && e && idx<4 && LOAD32(m)==3) {
            u64 fe=job+0xc0+(u64)idx*0x2d8,J=fe+0x48; u8 *q=bound(r,e,Q_RETAINED);
            if(q && LOAD64(J+8)==m && (LOAD32(J)&15)==0 && get32(q+0x70)==LOAD32(m+0x2508)) {
                if(LOAD32(fe+0x2d0)==0) nef_write(r,m,e,J,q);
                unbind(q);
                FREE_E(e);
                STORE64(r+0x748,0);
            }
        }
    }
    FREE_HDR(hres);
}
