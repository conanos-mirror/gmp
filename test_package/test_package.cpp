#include <gmp.h>

using namespace std;

int main (int argc, char **argv) {

  mpz_t a,b,c;
  mpz_inits(a,b,c,NULL);

  mpz_set_str(a, "1234", 10);
  return 0;
}
