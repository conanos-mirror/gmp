find_path(
  GMP_INCLUDE_DIR
  NAMES
  gmp.h
  PATHS
  include)

find_library(
  GMP_LIBRARY
  NAMES
  gmp
  libgmp
  PATHS
  lib)

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(GMP REQUIRED_VARS GMP_LIBRARY GMP_INCLUDE_DIR)
