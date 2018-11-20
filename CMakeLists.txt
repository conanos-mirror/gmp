cmake_minimum_required (VERSION 3.1)
project (gmp C)
set (MAJOR_VERSION 1)
set (MINOR_VERSION 6)
set (VERSION_PATCH 2)
set (VERSION 1.6.2)

OPTION(ENABLE_UNIT_TESTS "enable test ..." ON)
#
# Use Conan.io
#
if(USE_CONAN_IO)
    include(conanbuildinfo.cmake)
    conan_basic_setup()
    conan_define_targets()
endif()


if(NOT GMP_PROJECT_DIR)
  set(GMP_PROJECT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/gmp-${VERSION})
endif()

include(cmake/utils.cmake)

if(MSVC)   
   set(__arch__ x86)
   if(CMAKE_GENERATOR MATCHES Win64)
     set(__arch__ x86_64)
   endif()
   
   add_definitions(-D_CRT_SECURE_NO_WARNINGS)
   
   if(__arch__ STREQUAL x86)
    set(GMP_LIMB_BITS 32)
    set(GMP_NAIL_BITS 0)
	set(SIZEOF_MP_LIMB_T 4)
	set(SIZEOF_VOID_P 4)
   else()
    set(GMP_LIMB_BITS 64)
    set(GMP_NAIL_BITS 0)
	set(SIZEOF_MP_LIMB_T 8)
	set(SIZEOF_VOID_P 8)
	set(_LONG_LONG_LIMB_defination "#define _LONG_LONG_LIMB 1")
	add_definitions(-D_LONG_LONG_LIMB -D_LONG_LONG_LIMB=1)	 
   endif()

   add_definitions(/wd4018)
   add_definitions(/wd4273)
   add_definitions(/wd4090)
   add_definitions(/wd4013)
   add_definitions(/wd4244)
   add_definitions(/wd4311)
   add_definitions(/wd4267)
   add_definitions(/wd5999)
   add_definitions(/wd4146)
   add_definitions(/wd4819)
   add_definitions(/wd4101)
   add_definitions(/wd4334)

endif()



if(BUILD_SHARED_LIBS)
  set(__GMP_LIBGMP_DLL 1)
else()
  set(__GMP_LIBGMP_DLL 0)
endif()

add_definitions(-D__GMP_WITHIN_GMP)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/cmake/gmp.h.cmake    ${CMAKE_CURRENT_BINARY_DIR}/gmp.h @ONLY)
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/cmake/config.h.cmake ${CMAKE_CURRENT_BINARY_DIR}/config.h @ONLY)

include_directories(${GMP_PROJECT_DIR}
                    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/msvc
					${CMAKE_CURRENT_SOURCE_DIR}/cmake/msvc/${__arch__}
                    ${CMAKE_HOME_DIRECTORY}/mpn/generic
                    ${CMAKE_CURRENT_BINARY_DIR}
					)


set(_SOURCES #tal-debug.c
	${GMP_PROJECT_DIR}/assert.c
	${GMP_PROJECT_DIR}/errno.c 
	${GMP_PROJECT_DIR}/extract-dbl.c
	${GMP_PROJECT_DIR}/invalid.c
	${GMP_PROJECT_DIR}/memory.c
	${GMP_PROJECT_DIR}/mp_bpl.c
	${GMP_PROJECT_DIR}/mp_clz_tab.c
	${GMP_PROJECT_DIR}/mp_dv_tab.c
	${GMP_PROJECT_DIR}/mp_get_fns.c
	${GMP_PROJECT_DIR}/mp_minv_tab.c
	${GMP_PROJECT_DIR}/mp_set_fns.c
	${GMP_PROJECT_DIR}/nextprime.c
	${GMP_PROJECT_DIR}/primesieve.c
	${GMP_PROJECT_DIR}/tal-reent.c
	${GMP_PROJECT_DIR}/version.c )




file(GLOB _MPF_SRCS    ${GMP_PROJECT_DIR}/mpf/*.c)
file(GLOB _MPQ_SRCS    ${GMP_PROJECT_DIR}/mpq/*.c)
file(GLOB _MPZ_SRCS    ${GMP_PROJECT_DIR}/mpz/*.c)
file(GLOB _PRINTF_SRCS ${GMP_PROJECT_DIR}/printf/*.c)
file(GLOB _RAND_SRCS   ${GMP_PROJECT_DIR}/rand/*.c)
file(GLOB _SCANF_SRCS  ${GMP_PROJECT_DIR}/scanf/*.c)

file(GLOB _MPN_ARCH_SRCS ${CMAKE_CURRENT_SOURCE_DIR}/cmake/msvc/${__arch__}/*.c)
include(cmake/mpn-generic.cmake)
set(_SOURCES ${_SOURCES} ${MPN_GENERIC_SOURCES}  ${_MPN_ARCH_SRCS}
    ${_MPF_SRCS} ${_MPQ_SRCS} ${_MPZ_SRCS} 
	${_PRINTF_SRCS} ${_RAND_SRCS} ${_SCANF_SRCS}
	)

add_library(gmp ${_SOURCES})
assign_source_group(${_SOURCES})

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/gmp.h DESTINATION include)
INSTALL(TARGETS gmp
       RUNTIME DESTINATION bin
       LIBRARY DESTINATION lib
	   ARCHIVE DESTINATION lib )
	   
#enable_testing()
#add_subdirectory(tests)

if( ENABLE_UNIT_TESTS )

  enable_testing()
  include_directories(${GMP_PROJECT_DIR}/tests)

  set(GMP_TESTS_DIR "${GMP_PROJECT_DIR}/tests")
  add_library(libtests STATIC ${GMP_TESTS_DIR}/memory.c 
			  ${GMP_TESTS_DIR}/misc.c ${GMP_TESTS_DIR}/refmpf.c 
			  ${GMP_TESTS_DIR}/refmpn.c ${GMP_TESTS_DIR}/refmpq.c 
			  ${GMP_TESTS_DIR}/refmpz.c ${GMP_TESTS_DIR}/spinner.c 
			  ${GMP_TESTS_DIR}/trace.c)
  

	  #---------------------------#
	  #      make_test            #
	  #---------------------------#
  macro(make_test suite name)
	 set(dir ${ARGV2})
	 if(NOT dir)
	   set(dir ${GMP_TESTS_DIR}/${suite})
	 endif()
	 add_executable(${suite}-${name} ${dir}/${name}.c)
	 target_link_libraries(${suite}-${name} gmp libtests)
	 add_test(${suite}-${name} ${suite}-${name})
  endmacro()
  
  
  
  
  add_definitions(-D_USE_MATH_DEFINES)
  
				
  foreach(name t-bswap t-constants t-count_zeros
			   t-hightomask t-modlinv t-popc t-parity t-sub)
	  make_test(tests ${name} ${GMP_PROJECT_DIR}/tests)
  endforeach()  

	  #-------------------------------#
	  #       rand                    #
	  #-------------------------------#	
  add_library(libstat STATIC ${GMP_TESTS_DIR}/rand/gmpstat.h 
	  ${GMP_TESTS_DIR}/rand/statlib.c 
	  ${GMP_TESTS_DIR}/rand/zdiv_round.c)	  
  foreach(name t-iset t-lc2exp t-mt t-rand t-urbui t-urmui t-urndmm)   
	 make_test(rand ${name} )
	 target_link_libraries(rand-${name} libstat)
  endforeach()
	  #-------------------------------#
	  #       misc                    #
	  #-------------------------------#
  foreach(name t-printf t-scanf t-locale)
	make_test(misc ${name})
  endforeach()  
	  #-------------------------------#
	  #       mpf                     #
	  #-------------------------------#
  foreach(name t-dm2exp t-conv t-add t-sub t-sqrt t-sqrt_ui t-muldiv reuse 
			   t-cmp_d t-cmp_si t-div t-fits t-get_d t-get_d_2exp 
			   t-get_si t-get_ui t-gsprec t-inp_str t-int_p t-mul_ui 
			   t-set t-set_q t-set_si t-set_ui t-trunc t-ui_div t-eq t-pow_ui)			   
	   make_test(mpf ${name})
  endforeach()  
	  #-------------------------------#
	  #       mpn                     #
	  #-------------------------------#
  foreach(name t-asmtype t-aors_1 t-divrem_1 t-mod_1 t-fat t-get_d	
			   t-instrument t-iord_u t-mp_bases t-perfsqr t-scan logic		
			   t-toom22 t-toom32 t-toom33 t-toom42 t-toom43 t-toom44			
			   t-toom52 t-toom53 t-toom54 t-toom62 t-toom63 t-toom6h t-toom8h	
			   t-toom2-sqr t-toom3-sqr t-toom4-sqr t-toom6-sqr t-toom8-sqr		
			   t-div t-mul t-mullo t-sqrlo t-mulmod_bnm1 t-sqrmod_bnm1 t-mulmid	
			   t-hgcd t-hgcd_appr t-matrix22 t-invert t-bdiv				
			   t-broot t-brootinv t-minvert t-sizeinbase)			   
	  make_test(mpn ${name})
  endforeach()  
	  #-------------------------------#
	  #       mpq                     #
	  #-------------------------------#
  foreach(name t-aors t-cmp t-cmp_ui t-cmp_si t-equal t-get_d t-get_str
			   t-inp_str t-inv t-md_2exp t-set_f t-set_str io reuse t-cmp_z)			   
	  make_test(mpq ${name})
  endforeach()  
  
  add_definitions(-Dstrcasecmp=_stricmp)
  foreach(name reuse t-addsub t-cmp t-mul t-mul_i t-tdiv t-tdiv_ui t-fdiv 
			   t-fdiv_ui t-cdiv_ui t-gcd t-gcd_ui t-lcm t-invert dive dive_ui t-sqrtrem 
			   convert io t-inp_str logic bit t-powm t-powm_ui t-pow t-div_2exp      
			   t-root t-perfsqr t-perfpow t-jac t-bin t-get_d t-get_d_2exp t-get_si	
			   t-set_d t-set_si							
			   t-fac_ui t-mfac_uiui t-primorial_ui t-fib_ui t-lucnum_ui t-scan t-fits   
			   t-divis t-divis_2exp t-cong t-cong_2exp t-sizeinbase t-set_str        
			   t-aorsmul t-cmp_d t-cmp_si t-hamdist t-oddeven t-popcount t-set_f     
			   t-io_raw t-import t-export t-pprime_p t-nextprime t-remove t-limbs)
	  make_test(mpz ${name})
  endforeach()
endif()