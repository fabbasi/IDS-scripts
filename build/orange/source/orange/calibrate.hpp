/*
    This file is part of Orange.
    
    Copyright 1996-2010 Faculty of Computer and Information Science, University of Ljubljana
    Contact: janez.demsar@fri.uni-lj.si

    Orange is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Orange is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Orange.  If not, see <http://www.gnu.org/licenses/>.
*/


#ifndef __CALIBRATE_HPP
#define __CALIBRATE_HPP

#include "root.hpp"
#include "orvector.hpp"

WRAPPER(Classifier)
WRAPPER(ExampleGenerator)

class ORANGE_API TThresholdCA : public TOrange {
public:
  __REGISTER_CLASS

  float operator()(PClassifier, PExampleGenerator, const int &weighID, float &optCA, const int &targetValue = -1, TFloatFloatList *CAs = NULL);
};

#endif
