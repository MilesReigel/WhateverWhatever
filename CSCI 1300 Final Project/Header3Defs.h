#include <string>
#ifndef HEADER3D_H
#define HEADER3D_H

using namespace std;

int Character1 = 0, Character2 = 0;
int statMinimum = 100;

class Characters { 
public:
    Characters(int character);
    void PathSelection();
    void PrintStats(int player);

    string name, advisor;
    int Dsp, Exp, Acc, Eff, Ins;
    bool path;
};

#endif
