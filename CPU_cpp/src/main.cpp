#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    int i = 1;
    while (true) {
        print(generateKey(state));
        inputAdd(state, history);
        if (i % 3 == 0) {
            inputRemove(state, history);
        }
        i++;
    }

    return 0;
}