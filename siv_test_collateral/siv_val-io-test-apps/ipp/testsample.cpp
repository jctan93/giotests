// Measure FFT performance //

#include <stdio.h>
#include "math.h"
#include "ipp.h"

int main()
{

  //Get the version of IPP on this machine
  const IppLibraryVersion* lib;
  lib = ippsGetLibVersion();

  //Measure FFT performance
  #define Nord 10  
  #define LEN  1024
  #define IPP_PI    ( 3.14159265358979323846 )
  Ipp32f  Signal[LEN],SignalFft[LEN];
  Ipp32f  Amp=1;
  Ipp32f  fsample=51.2e6;
  Ipp32f  fc=3e6;
    
  int NoFFT=100000; 
  int   i;
  IppsFFTSpec_R_32f* FftSpec;
  Ipp8u * pFFTInitBuf, *pFFTWorkBuf, *pFFTSpecBuf;
  int FftOrder=Nord;
  int FftFlag=IPP_FFT_DIV_FWD_BY_N;
  int SpecSize, SpecBufferSize, BufferSize;
  IppStatus Status;  

    
  // Generate sine wave 
  for (i=0;i<LEN;i++)
  {  Signal[i]=Amp*cos(2*IPP_PI*i*fc/fsample);
  }
  
  ippsFFTGetSize_R_32f(FftOrder, FftFlag, ippAlgHintNone, &SpecSize, &SpecBufferSize, &BufferSize);

  pFFTSpecBuf = ippsMalloc_8u(SpecSize);
  pFFTInitBuf = ippsMalloc_8u(SpecBufferSize);
  pFFTWorkBuf = ippsMalloc_8u(BufferSize);
 
  ippsFFTInit_R_32f(&FftSpec, FftOrder, FftFlag, ippAlgHintNone, pFFTSpecBuf, pFFTInitBuf);
  
  Status= ippsFFTFwd_RToPack_32f(Signal, SignalFft, FftSpec, pFFTWorkBuf);
  
  if(Status == 0){
    printf("%s\n","TEST PASSED");
  }else{
    printf("%s\n","TEST FAILED");
  }

  printf("IPP Version     :%s\n",lib->Version);
  printf("IPP Opt Code    :%s\n",lib->Name);
  
  ippsFree(pFFTSpecBuf);
  ippsFree(pFFTInitBuf);
  ippsFree(pFFTWorkBuf);

  return 0;
}
