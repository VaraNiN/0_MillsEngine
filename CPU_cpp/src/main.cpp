#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    while (true) {
        print(generateKey(state));
        inputAdd(state, history);
    }

    return 0;
}