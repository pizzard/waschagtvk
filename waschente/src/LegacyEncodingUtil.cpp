#include <vector>
#include <algorithm>
#include <iconv.h>  // GNU ICONV(3)
#include "LegacyEncodingUtil.h"

std::string _conv(const std::string in, const char* tocode, const char* fromcode) {
        auto cd = iconv_open(tocode, fromcode);
        std::vector<char> invec;
        auto inbytesleft = in.length();
	invec.reserve(inbytesleft);
        std::copy(in.begin(), in.end(), invec.begin());
        auto inbuf = invec.data();  // cannot be const for using iconv
        std::vector<char> outvec;
        auto outbytesleft = 2 * inbytesleft;
	outvec.reserve(outbytesleft);
        auto outbuf = outvec.data();  // need to do AFTER reserve
        /*auto len =*/ iconv(cd, &inbuf, &inbytesleft, &outbuf, &outbytesleft);
	/*
	if(len > (size_t) in.length() || len == 0) {  // on error (ignoring)
		len = in.length();
	}
	*/
	auto len = 2 * in.length() - outbytesleft;
        iconv_close(cd);
        return std::string(outvec.data(), len);  // outbuf can be moved by iconv
}

std::string legacyenc::decode(const std::string in) {
	return _conv(in, "CP1252", "UTF8");
}

std::string legacyenc::encode(const std::string in) {
	return _conv(in, "UTF8", "CP1252");
}
