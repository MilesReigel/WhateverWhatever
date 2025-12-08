#include <string>
#include <windows.h>
#ifndef HEADER3D_H
#define HEADER3D_H

using namespace std;

int Character1 = 0, Character2 = 0;
int statMinimum = 100;
int second = 1000;

class Characters { 
public:
    Characters();
    Characters(int player, int character);
    void PathSelection(int player);
    void PrintStats(int player, int typeOfCall);
    void AdvisorSelection(int player);
    string AdvisorPrinting(int advisor);
    void misfortune(int player, Characters p1, Characters p2);
    void events(int player, Characters p1, Characters p2);    

    string name;
    int Dsp, Exp, Acc, Eff, Ins, number, advisor;
    bool path, theft, trapAhead;
};

void DspAddition(int player, int amount, Characters p1, Characters p2);

#endif
