#include <iostream>
#include <string>
#include "Board.cpp"
#include "OtherHeader.cpp"

using namespace std;

int main() {
    //choose characters
    CharacterSelection();
    Characters p1(Character1);
    Characters p2(Character2);

    //choose path
    p1.PathSelection();
    p2.PathSelection();

    return(0);
}