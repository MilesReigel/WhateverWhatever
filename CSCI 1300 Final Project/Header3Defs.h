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
    Characters(int player, int character);
    void PathSelection(int player);
    void PrintStats(int player, int typeOfCall);
    void AdvisorSelection(int player);
    string AdvisorPrinting(int advisor);
    void misfortune(int player);
    void events();    

    string name;
    int Dsp, Exp, Acc, Eff, Ins, number, advisor;
    bool path;
};

#endif
