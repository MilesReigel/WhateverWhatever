#include <iostream>
#include <fstream>
using namespace std;

string text;

int main()
{
    fstream BudgetFile("Budget.txt");

    while (getline(BudgetFile, text))
    {
        cout << text;
    }

    BudgetFile.close();

    return(0);
}