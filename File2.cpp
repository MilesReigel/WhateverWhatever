#include <iostream>
using namespace std;

struct MRRB {int xposition; int yposition;};
string inputstr = "123 456";

MRRB strtoint(string str) {
    int xposition = (int(str[0] - '0') * 100) + (int(str[1] - '0') * 10) + int(str[2] - '0');
    int yposition = (int(str[4] - '0') * 100) + (int(str[5] - '0') * 10) + int(str[6] - '0');
    return MRRB{xposition, yposition};
}

int main()
{
    MRRB positions = strtoint(inputstr);
    cout << positions.xposition << "." << positions.yposition << endl;
}