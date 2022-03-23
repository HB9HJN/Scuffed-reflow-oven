#include <iostream>
#include <sstream>
#include <string>

int main(){
		std::string cmd = "sigrok-cli --driver=uni-t-ut61e:conn=1a86.e008 --samples 1"; 
		std::string data;
		FILE * stream;
		const int max_buffer = 256;
		char buffer[max_buffer];
		cmd.append(" 2>&1");

		stream = popen(cmd.c_str(), "r");
									
		if (stream){
			while (!feof(stream))
			if (fgets(buffer, max_buffer, stream) != NULL) data.append(buffer);
				pclose(stream);
		}

		std::cout << data; 

}
