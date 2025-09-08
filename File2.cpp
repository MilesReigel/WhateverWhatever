#include <iostream>

using namespace std;

class Dog
{
    public:
        void bark()
        {
            cout << "Woof!" << endl;
        }
};


int main()
{
    Dog hound;
    hound.bark();    
    return (0);
}
