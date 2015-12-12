#ifndef CRYPT_INCLUDE_
#define CRYPT_INCLUDE_

//
// This program implements the Proposed Federal Information Processing Data
// Encryption Standard. See Federal Register, March 17, 1975 (40FR12134)
//

//
// Initial permutation
//

#include <sys/types.h>

void setkey_r(struct sched *sp, const char *key);

void encrypt_r(struct sched *sp, char *block, int edflag);

char *crypt_r(const char *key, const char *salt, char *buf);

#endif

