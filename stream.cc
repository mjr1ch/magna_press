#include <stdint.h>
#include <stddef.h>
#include "pru_uart.h"
#include "pru_ecap.h" 

struct Message {
	uint32_t id;
	uint32_t timestamp;
	uint32_t position;
	int32_t force;
};

// encoder position in other PRU core's memory
#define position_var ((uint32_t const volatile *)0x00002000)

// layout of shared ddr3 memory (filled in by loader)
struct DDRLayout {
	Message volatile *msgbuf;
	uint16_t num_msgs;
	uint16_t msg_size;
};

struct SharedVars {
	// set by pru before halting
	char const *abort_file;
	int abort_line;
	// read-pointer updated by python
	uint16_t ridx;
};

far struct DDRLayout ddr __attribute__((location(0x10000))) = {};
far struct SharedVars volatile shmem __attribute__((location(0x10100))) = {};

static inline uint32_t timestamp_cycles()
{
    return CT_ECAP.TSCTR;
}

uint32_t timestamp()
{
    static uint32_t now = 0;
    return now += (uint16_t)( ( timestamp_cycles() >> 16 ) - now );
}


// for easier debugging, record where in the source code we halted
__attribute__((noreturn))
void abort_at( char const *file, int line )
{
	shmem.abort_file = file;
	shmem.abort_line = line;
	for(;;) __halt();
}

static inline void assert_at( bool cond, char const *file, int line )
{
	if( ! cond )
		abort_at( file, line );
}

#define abort() abort_at( __FILE__, __LINE__ )
#define assert(cond) assert_at( (cond), __FILE__, __LINE__ )

// local copy of write-pointer
static uint16_t widx = 0;

// global var for write-pointer is located right after message ringbuffer
#define ddr_msgbuf_end	( ddr.msgbuf + ddr.num_msgs )
#define ddr_widx	( *(uint16_t volatile *)ddr_msgbuf_end )

// receive byte from uart
static inline char uart_recv_byte()
{
    for(;;) {
        uint8_t lsr = CT_UART.LSR;
        if( lsr & 0x1e )
            abort();  // receive-error occurred
        if( lsr & 0x01 )
            return (char) CT_UART.RBR;
    }
}


// receive CR-terminated line from uart
static inline uint8_t uart_recv_line( char volatile msg[], uint8_t maxlen )
{
    uint8_t len = 0;

    for(;;) {
        char c = uart_recv_byte();
        if( c == '\r' )
            break;  // found end of line
        if( len == maxlen )
            abort();  // line does not fit in buffer
        msg[ len++ ] = c;
    }

    return len;
}

int32_t receive_measurement()
{
    // allocate buffer at fixed address for debugging convenience
    static char volatile msg[8] __attribute__((location(0x1f00)));

    // receive line from uart
    uint8_t len = uart_recv_line( msg, sizeof msg );

    // verify length and prefix
    if( len != 8 || msg[0] != 'N' || (msg[1] != '+' && msg[1] != '-'))
        abort();

    // parse the remainder as integer
    int32_t value = 0;
    uint8_t i;
    for( i = 2; i < len; i++ ) {
        if( msg[i] < '0' || msg[i] > '9' )
            abort();
        value = value * 10 + ( msg[i] - '0' );
    }
    if (msg[1] == '-')
            value *= -1;

    return value;
}


void initialize()
{
	// perform sanity-checking
	assert( 0x80000000 <= (uint32_t)ddr.msgbuf );
	assert( ddr.msgbuf < ddr_msgbuf_end );
	assert( ddr.msg_size == sizeof(Message) );

	assert( ddr_widx == widx );
	assert( shmem.ridx == widx );
}


static inline uint16_t next_idx( uint16_t idx )
{
	if( ++idx == ddr.num_msgs )
		idx = 0;
	return idx;
}


void send_message( uint32_t id)
{
	uint16_t next_widx = next_idx( widx );

	if( next_widx == shmem.ridx ) {
		// can't send message, ringbuffer is full
		abort();
	}

	Message volatile *msg = &ddr.msgbuf[ widx ];

	// fill in contents of message
	msg->id = id;
	msg->position = *position_var;
	msg->force = receive_measurement();
	msg->timestamp = timestamp();
	// update write-pointer
	ddr_widx = widx = next_widx;
}

void main() {
	initialize();

	CT_UART.THR = 'S';
    CT_UART.THR = 'N';
    CT_UART.THR = '\r';

	uint32_t id = 0;
	for(;;) {
		send_message( ++id );
		__delay_cycles( 10000 );
	}
}
