/**
 * Copyright (c) 2011 Baidu.com, Inc. All Rights Reserved
 */
/* vim: set ts=4 sw=4 sts=4 tw=80 noet: */
/**
 * @file coor_bd2gcj.cpp
 * @brief transform siwei-coordsys to online-mercator coordsys.
 * @detail /dataproc/siwei/basic/coor_bd2gcj.cpp 
 * @author liangwei03
 * @date 2011-4-22
 */
#include <iostream>
#include <string>
#include <vector>

#include "coordtrans.cpp"

using namespace std;

void SplitString(const std::string& s, std::vector<std::string>& v, const std::string& c)
{
	string::size_type pos1, pos2;
	pos2 = s.find(c);
	pos1 = 0;
	while(string::npos != pos2)
	{
		v.push_back(s.substr(pos1, pos2-pos1));
						   
		pos1 = pos2 + c.size();
		pos2 = s.find(c, pos1);
								    }
		if(pos1 != s.length())
			v.push_back(s.substr(pos1));
}

int main(int argc, char* argv[]) {
	double oldLng;
	double oldLat;
	double newLng;
	double newLat;
	string xyPtr;
	string str(argv[3]);
	vector<string> result; 
	SplitString(str, result, "G");

	for (int i = 0; i < result.size(); ++i)
	{
		if (result[i].empty())
		{
			continue;
		}
		xyPtr = result[i];
		size_t iPos = xyPtr.find(",");
        oldLng = atof(xyPtr.substr(0, iPos).c_str());
        oldLat = atof(xyPtr.substr(iPos + 1, xyPtr.length() - iPos - 1).c_str());
        coordtrans(argv[1], argv[2], oldLng, oldLat, newLng, newLat);
    	printf("%lf,%lf,",newLng,newLat);
	}
	printf("\n");
	return 0;
}
