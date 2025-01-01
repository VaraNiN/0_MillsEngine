#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"

int main() {
    BoardState state;
    state.whitePieces.set(5);
    state.blackPieces.set(6);
    int inputs = 24;
    std::vector<int> result = runMillsBoard(state, inputs);

    for (int index : result) {
        std::cout << "Clicked vicinity: " << index << "\n";
    }

    return 0;
}