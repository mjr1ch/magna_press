#include "common.h"
 
 #define counter r10
 #define pin_A   r31.t2
 #define pin_B   r31.t16
 
 .macro increment
     add     counter, counter, 1
     sbco    &counter, c28, 0, 4     // store counter to memory
 .endm
 
 .macro decrement
     sub     counter, counter, 1
     sbco    &counter, c28, 0, 4     // store counter to memory
 .endm
 
 
     mov     counter, 0
     sbco    &counter, c28, 0, 4     // store initial counter to memory
 
 // jump into right place of the loop based on initial state of A
     bbs     Ahigh,    pin_A
     jmp     Alow
 
 A0_Bfall:
     increment                       // B falling edge with A low
 
 Alow:
     wbs     pin_A                   // A is low, wait for A rise
     bbs     Arise_B1, pin_B         // A rising edge, check B
 
     increment                       // A rising edge with B low
     jmp     Blow
 
 
 Afall_B0:
     decrement                       // A falling edge with B low
 
 Blow:
     wbs     pin_B                   // B is low, wait for B rise
     bbs     A1_Brise, pin_A         // B rising edge, check A
 
 
     decrement                       // B rising edge with A low
     jmp     Alow
 
 A1_Brise:
     increment                       // B rising edge with A high
 
 Ahigh:
     wbc     pin_A                   // A is high, wait for A fall
     bbc     Afall_B0, pin_B         // A falling edge, check B
 
     increment                       // A falling edge with B high             
     jmp     Bhigh 
                                                              
 Arise_B1: 
     decrement                       // A rising edge wit 
      
 Bhigh:   
     wbc     pin_B                   // B is high, wait for B fall 
     bbc     A0_Bfall, pin_A         // B falling edge, check A 
                                                                      
     decrement                       // B falling edge with A high 
     jmp     Ahigh

