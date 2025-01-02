#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    for (int i = 0; i < 16; i++) {
        state.whitePieces = state.possibleMills[i];
        show_position(state);
    }

    return 0;
}