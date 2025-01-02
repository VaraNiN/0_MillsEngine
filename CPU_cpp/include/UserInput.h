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

void inputAdd(BoardState& state, History& history);

void inputRemove(BoardState& state, History& history);

void inputMove(BoardState& state, History& history);

#endif // USERINPUT_H