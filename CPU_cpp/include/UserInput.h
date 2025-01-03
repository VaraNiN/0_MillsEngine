#ifndef USERINPUT_H
#define USERINPUT_H

#include "Engine.h"
#include "GUI.h"
#include <bitset>
#include <string>
#include <sstream>
#include <vector>
#include <cstdint>
#include <iostream>
#include <cstdlib>


int inputAdd(BoardState& state, History& history);

void inputRemove(BoardState& state, History& history);

int inputMove(BoardState& state, History& history);

void playerMove(BoardState& state, History& history);

#endif // USERINPUT_H