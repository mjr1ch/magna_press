#include <stdint.h>
#include "pru_uart.h"
 
typedef uint8_t u8;
 

// receive byte from uart
static inline char uart_recv_byte()
{
    for(;;) {
        u8 lsr = CT_UART.LSR;
        if( lsr & 0x1e )
            __halt();  // receive-error occurred
        if( lsr & 0x01 )
            return (char) CT_UART.RBR;
    }
}
 
// receive CR-terminated line from uart
static inline unsigned uart_recv_line( char msg[], u8 maxlen )
{
    u8 len = 0;
 
    for(;;) {
        char c = uart_recv_byte();
        if( c == '\r' )
            break;  // found end of line
        if( len == maxlen )
            __halt();  // line does not fit in buffer
        msg[ len++ ] = c;
    }
 
    return len;
}
 
void main()
{
    static char msg[24];
 
    for(;;) {
        u8 len = uart_recv_line( msg, sizeof msg );
 
        // parse and interpret message from load cell
 
        // read position value from decoder and run control loop
 
        // update pwm output
    }
}
