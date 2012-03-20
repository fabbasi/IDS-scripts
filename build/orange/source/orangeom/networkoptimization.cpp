/*
    This file is part of Orange.
    
    Copyright 1996-2010 Faculty of Computer and Information Science, University of Ljubljana
    Author: Miha Stajdohar, 1996--2010
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


#include "ppp/networkoptimization.ppp"
#define PI 3.14159265

TNetworkOptimization::TNetworkOptimization()
{

	//cout << "TNetworkOptimization::constructor" << endl;
	import_array();

	nVertices = 0;
	nLinks = 0;

	k = 1;
	k2 = 1;
	width = 10000;
	height = 10000;
  tree = NULL;
	temperature = sqrt(width*width + height*height) / 10;
	coolFactor = 0.96;

	//cout << "constructor end" << endl;
}

#ifdef _MSC_VER
#if _MSC_VER < 1300
template<class T>
inline T &min(const T&x, const T&y)
{ return x<y ? x : y; }
#endif
#endif

TNetworkOptimization::~TNetworkOptimization()
{
	//cout << "destructor" << endl;
}

void TNetworkOptimization::dumpCoordinates()
{
	int rows = nVertices;
	int columns = 2;

	for (int i = 0; i < rows; i++)
	{
		for (int j = 0; j < columns; j++)
		{
			cout << network->pos[j][i] << "  ";
		}

		cout << endl;
	}
}

void TNetworkOptimization::random()
{
	//cout << "random" << endl;
	if (!network)
	{
		cout << "random::network is NULL" << endl;
		return;
	}

	srand(time(NULL));
	int i;
	for (i = 0; i < nVertices; i++)
	{
		network->pos[0][i] = rand() % (int)width;
		network->pos[1][i] = rand() % (int)height;
	}
	//cout << "random end" << endl;



}

int TNetworkOptimization::circularCrossingReduction()
{
	vector<QueueVertex*> vertices;
	vector<QueueVertex*> original;

	int i;
	for (i = 0; i < nVertices; i++)
	{
		vector<int> neighbours;
		network->getNeighbours(i, neighbours);

		QueueVertex *vertex = new QueueVertex();
		vertex->ndx = i;
		vertex->unplacedNeighbours = neighbours.size();
		vertex->neighbours = neighbours;

		vertices.push_back(vertex);
	}
	original.assign(vertices.begin(), vertices.end());

	deque<int> positions;
	while (vertices.size() > 0)
	{
		sort(vertices.begin(), vertices.end(), QueueVertex());
		QueueVertex *vertex = vertices.back();


		// update neighbours
		for (i = 0; i < vertex->neighbours.size(); i++)
		{
			int ndx = vertex->neighbours[i];

			original[ndx]->placedNeighbours++;
			original[ndx]->unplacedNeighbours--;
		}

		// count left & right crossings
		if (vertex->placedNeighbours > 0)
		{
			int left = 0;
			vector<int> lCrossings;
			vector<int> rCrossings;
			for (i = 0; i < positions.size(); i++)
			{
				int ndx = positions[i];

				if (vertex->hasNeighbour(ndx))
				{
					lCrossings.push_back(left);
					left += original[ndx]->unplacedNeighbours;
					rCrossings.push_back(left);
				}
				else
					left += original[ndx]->unplacedNeighbours;
			}

			int leftCrossings = 0;
			int rightCrossings = 0;

			for (i = 0; i < lCrossings.size(); i++)
				leftCrossings += lCrossings[i];

			rCrossings.push_back(left);
			for (i = rCrossings.size() - 1; i > 0 ; i--)
				rightCrossings += rCrossings[i] - rCrossings[i - 1];
			//cout << "left: " << leftCrossings << " right: " <<rightCrossings << endl;
			if (leftCrossings < rightCrossings)
				positions.push_front(vertex->ndx);
			else
				positions.push_back(vertex->ndx);

		}
		else
			positions.push_back(vertex->ndx);

		vertices.pop_back();
	}

	// Circular sifting
	for (i = 0; i < positions.size(); i++)
		original[positions[i]]->position = i;

	int step;
	for (step = 0; step < 5; step++)
	{
		for (i = 0; i < nVertices; i++)
		{
			bool stop = false;
			int switchNdx = -1;
			QueueVertex *u = original[positions[i]];
			int vNdx = (i + 1) % nVertices;

			while (!stop)
			{
				QueueVertex *v = original[positions[vNdx]];

				int midCrossings = u->neighbours.size() * v->neighbours.size() / 2;
				int crossings = 0;
				int j,k;
				for (j = 0; j < u->neighbours.size(); j++)
					for (k = 0; k < v->neighbours.size(); k++)
						if ((original[u->neighbours[j]]->position == v->position) || (original[v->neighbours[k]]->position == u->position))
							midCrossings = (u->neighbours.size() - 1) * (v->neighbours.size() - 1) / 2;
						else if ((original[u->neighbours[j]]->position + nVertices - u->position) % nVertices < (original[v->neighbours[k]]->position + nVertices - u->position) % nVertices)
							crossings++;

				//cout << "v: " <<  v->ndx << " crossings: " << crossings << " u.n.size: " << u->neighbours.size() << " v.n.size: " << v->neighbours.size() << " mid: " << midCrossings << endl;
				if (crossings > midCrossings)
					switchNdx = vNdx;
				else
					stop = true;

				vNdx = (vNdx + 1) % nVertices;
			}
			int j;
			if (switchNdx > -1)
			{
				//cout << "u: " << u->ndx << " switch: " << original[switchNdx]->ndx << endl << endl;
				positions.erase(positions.begin() + i);
				positions.insert(positions.begin() + switchNdx, u->ndx);

				for (j = i; j <= switchNdx; j++)
					original[positions[j]]->position = j;
			}
			//else
			//	cout << "u: " << u->ndx << " switch: " << switchNdx << endl;
		}
	}

	int xCenter = width / 2;
	int yCenter = height / 2;
	int r = (width < height) ? width * 0.38 : height * 0.38;

	double fi = PI;
	double fiStep = 2 * PI / nVertices;

	for (i = 0; i < nVertices; i++)
	{
		network->pos[0][positions[i]] = r * cos(fi) + xCenter;
		network->pos[1][positions[i]] = r * sin(fi) + yCenter;

		fi = fi - fiStep;
	}

	for (vector<QueueVertex*>::iterator i = original.begin(); i != original.end(); ++i)
		delete *i;

	original.clear();
	vertices.clear();

	return 0;
}

// type
// 0 - original
// 1 - random
int TNetworkOptimization::circular(int type)
{
	int xCenter = width / 2;
	int yCenter = height / 2;
	int r = (width < height) ? width * 0.38 : height * 0.38;

	int i;
	double fi = PI;
	double step = 2 * PI / nVertices;

	srand(time(NULL));
	vector<int> vertices;
	if (type == 1)
		for (i = 0; i < nVertices; i++)
			vertices.push_back(i);

	for (i = 0; i < nVertices; i++)
	{
		if (type == 0)
		{
			network->pos[0][i] = r * cos(fi) + xCenter;
			network->pos[1][i] = r * sin(fi) + yCenter;
		}
		else if (type == 1)
		{
			int ndx = rand() % vertices.size();

			network->pos[0][vertices[ndx]] = r * cos(fi) + xCenter;
			network->pos[1][vertices[ndx]] = r * sin(fi) + yCenter;

			vertices.erase(vertices.begin() + ndx);
		}

		fi = fi - step;
	}

	return 0;
}
int TNetworkOptimization::fruchtermanReingold(int steps, bool weighted)
{
	/*
	cout << "nVertices: " << nVertices << endl << endl;
	dumpCoordinates();
	/**/
	double **disp = (double**)malloc(nVertices * sizeof (double));
	int i = 0;
	for (i = 0; i < nVertices; i++)
	{
		disp[i] = (double *)calloc(2, sizeof(double));

		if (disp[i] == NULL)
		{
			cerr << "Couldn't allocate memory (disp[])\n";
			return 1;
		}
	}

	int count = 0;
	double kk = 1;
	double localTemparature = 5;
	double area = width * height;

	k2 = area / nVertices;
	k = sqrt(k2);
	kk = 2 * k;
	double kk2 = kk * kk;

	// iterations
	for (i = 0; i < steps; i++)
	{
		//cout << "iteration: " << i << endl;
		// reset disp
		int j = 0;
		for (j = 0; j < nVertices; j++)
		{
			disp[j][0] = 0;
			disp[j][1] = 0;
		}

		int v = 0;
		// calculate repulsive force
		//cout << "repulsive" << endl;
		for (v = 0; v < nVertices - 1; v++)
		{
			for (int u = v + 1; u < nVertices; u++)
			{
				double difX = network->pos[0][v] - network->pos[0][u];
				double difY = network->pos[1][v] - network->pos[1][u];

				double dif2 = difX * difX + difY * difY;

				if (dif2 < kk2)
				{
					if (dif2 == 0)
						dif2 = 1;

					double dX = difX * k2 / dif2;
					double dY = difY * k2 / dif2;

					disp[v][0] = disp[v][0] + dX;
					disp[v][1] = disp[v][1] + dY;

					disp[u][0] = disp[u][0] - dX;
					disp[u][1] = disp[u][1] - dY;
				}
			}
		}
		// calculate attractive forces
		//cout << "attractive" << endl;
		if (weighted)
		{
			for (j = 0; j < nLinks; j++)
			{
				int v = links[0][j];
				int u = links[1][j];

				double difX = network->pos[0][v] - network->pos[0][u];
				double difY = network->pos[1][v] - network->pos[1][u];

				double dif = sqrt(difX * difX + difY * difY);

				double *w = network->getEdge(v,u);
				double wsum = 0;
				int k;
				for (k=0; k < network->nEdgeTypes; k++) {
					wsum += w[k];
				}

				double dX = difX * dif / k * wsum;
				double dY = difY * dif / k * wsum;

				disp[v][0] = disp[v][0] - dX;
				disp[v][1] = disp[v][1] - dY;

				disp[u][0] = disp[u][0] + dX;
				disp[u][1] = disp[u][1] + dY;
			}
		}
		else
		{
			for (j = 0; j < nLinks; j++)
			{
				int v = links[0][j];
				int u = links[1][j];

				double difX = network->pos[0][v] - network->pos[0][u];
				double difY = network->pos[1][v] - network->pos[1][u];

				double dif = sqrt(difX * difX + difY * difY);

				double dX = difX * dif / k;
				double dY = difY * dif / k;

				disp[v][0] = disp[v][0] - dX;
				disp[v][1] = disp[v][1] - dY;

				disp[u][0] = disp[u][0] + dX;
				disp[u][1] = disp[u][1] + dY;
			}
		}
		//cout << "limit" << endl;
		// limit the maximum displacement to the temperature t
		// and then prevent from being displaced outside frame
		for (v = 0; v < nVertices; v++)
		{
			double dif = sqrt(disp[v][0] * disp[v][0] + disp[v][1] * disp[v][1]);

			if (dif == 0)
				dif = 1;

			network->pos[0][v] = network->pos[0][v] + (disp[v][0] * min(fabs(disp[v][0]), temperature) / dif);
			network->pos[1][v] = network->pos[1][v] + (disp[v][1] * min(fabs(disp[v][1]), temperature) / dif);

			//pos[v][0] = min((double)width,  max((double)0, pos[v][0]));
			//pos[v][1] = min((double)height, max((double)0, pos[v][1]));
		}
		//cout << temperature << ", ";
		temperature = temperature * coolFactor;
	}

	//cout << "end coors: " << endl;
	//dumpCoordinates();

	// free space
	for (i = 0; i < nVertices; i++)
	{
		free(disp[i]);
		disp[i] = NULL;
	}
	//cout << endl;
	free(disp);
	disp = NULL;

	return 0;
}


int TNetworkOptimization::radialFruchtermanReingold(int steps, int nCircles)
{
	/*
	cout << "nVertices: " << nVertices << endl << endl;
	dumpCoordinates();
	/**/
	double **disp = (double**)malloc(nVertices * sizeof (double));
	int i = 0;

	for (i = 0; i < nVertices; i++)
	{
		disp[i] = (double *)calloc(2, sizeof(double));

		if (disp[i] == NULL)
		{
			cerr << "Couldn't allocate memory (disp[])\n";
			return 1;
		}
	}

	int radius = width / nCircles / 2;
	//cout << "radius: " << radius << endl;
	int count = 0;
	double kk = 1;
	double localTemparature = 5;
	double area = width * height;

	k2 = area / nVertices;
	k = sqrt(k2);
	kk = 2 * k;
	double kk2 = kk * kk;
	// iterations
	for (i = 0; i < steps; i++)
	{
		//cout << "iteration: " << i << endl;
		// reset disp
		int j = 0;
		for (j = 0; j < nVertices; j++)
		{
			disp[j][0] = 0;
			disp[j][1] = 0;
		}

		int v = 0;
		// calculate repulsive force
		for (v = 0; v < nVertices - 1; v++)
		{
			for (int u = v + 1; u < nVertices; u++)
			{
				// only for vertices on the same level
				//if (level[v] != level[u])
				//	continue;

				if (level[u] == level[v])
					k = kVector[level[u]];
				else
					k = radius;

				//kk = 2 * k;
				k2 = k*k;

				double difX = network->pos[0][v] - network->pos[0][u];
				double difY = network->pos[1][v] - network->pos[1][u];

				double dif2 = difX * difX + difY * difY;

				if (dif2 < kk2)
				{
					if (dif2 == 0)
						dif2 = 1;

					double dX = difX * k2 / dif2;
					double dY = difY * k2 / dif2;

					disp[v][0] = disp[v][0] + dX;
					disp[v][1] = disp[v][1] + dY;

					disp[u][0] = disp[u][0] - dX;
					disp[u][1] = disp[u][1] - dY;
				}
			}
		}
		// calculate attractive forces
		for (j = 0; j < nLinks; j++)
		{
			int v = links[0][j];
			int u = links[1][j];

			// only for vertices on the same level
			//if (level[v] != level[u])
			//	continue;

			if (level[u] == level[v])
					k = kVector[level[u]];
				else
					k = radius;

			kk = 2 * k;
			k2 = k*k;

			double difX = network->pos[0][v] - network->pos[0][u];
			double difY = network->pos[1][v] - network->pos[1][u];

			double dif = sqrt(difX * difX + difY * difY);

			double dX = difX * dif / k;
			double dY = difY * dif / k;

			disp[v][0] = disp[v][0] - dX;
			disp[v][1] = disp[v][1] - dY;

			disp[u][0] = disp[u][0] + dX;
			disp[u][1] = disp[u][1] + dY;
		}
		// limit the maximum displacement to the temperature t
		// and then prevent from being displaced outside frame

		for (v = 0; v < nCircles; v++)
		{
			levelMin[v] = INT_MAX;
			levelMax[v] = 0;
		}

		for (v = 0; v < nVertices; v++)
		{
			double dif = sqrt(disp[v][0] * disp[v][0] + disp[v][1] * disp[v][1]);

			if (dif == 0)
				dif = 1;

			network->pos[0][v] = network->pos[0][v] + (disp[v][0] * min(fabs(disp[v][0]), temperature) / dif);
			network->pos[1][v] = network->pos[1][v] + (disp[v][1] * min(fabs(disp[v][1]), temperature) / dif);

			double distance = (network->pos[0][v] - (width/2)) * (network->pos[0][v] - (width/2)) + (network->pos[1][v] - (height/2)) * (network->pos[1][v] - (height/2));

			if (distance < levelMin[level[v]])
				levelMin[level[v]] = distance;

			if (distance > levelMax[level[v]])
				levelMax[level[v]] = distance;
		}

		for (v = 1; v < nCircles; v++)
		{
			//cout << "c: " << v << " min: " << sqrt(levelMin[v]) << " max: " << sqrt(levelMax[v]);

			levelMin[v] = (v - 1) * radius / sqrt(levelMin[v]);
			levelMax[v] =  v      * radius / sqrt(levelMax[v]);

			//cout  << " min: " << levelMin[v] << " max: " << levelMax[v] << "r: " << v * radius << endl;
		}

		for (v = 0; v < nVertices; v++)
		{
			double distance = sqrt((network->pos[0][v] - (width/2)) * (network->pos[0][v] - (width/2)) + (network->pos[1][v] - (height/2)) * (network->pos[1][v] - (height/2)));

			if (level[v] == 0)
			{
				// move to center
				network->pos[0][v] = width / 2;
				network->pos[1][v] = height / 2;

				//cout << "center, x: " << pos[v][0] << " y: " << pos[v][1] << endl;
			}
			else if (distance > level[v] * radius - radius / 2)
			{
				// move to outer ring
				if (levelMax[level[v]] < 1)
				{
					double fi = 0;
					double x = network->pos[0][v] - (width / 2);
					double y = network->pos[1][v] - (height / 2);

					if (x < 0)
						fi = atan(y / x) + PI;
					else if ((x > 0) && (y >= 0))
						fi = atan(y / x);
					else if ((x > 0) && (y < 0))
						fi = atan(y / x) + 2 * PI;
					else if ((x == 0) && (y > 0))
						fi = PI / 2;
					else if ((x == 0) && (y < 0))
						fi = 3 * PI / 2;

					network->pos[0][v] = levelMax[level[v]] * distance * cos(fi) + (width / 2);
					network->pos[1][v] = levelMax[level[v]] * distance * sin(fi) + (height / 2);

					//cout << "outer, x: " << pos[v][0] << " y: " << pos[v][1] << " radius: " << radius << " fi: " << fi << " level: " << level[v] << " v: " << v << endl;
				}
			}
			else if (distance < (level[v] - 1) * radius + radius / 2)
			{
				// move to inner ring
				if (levelMin[level[v]] > 1)
				{
					double fi = 0;
					double x = network->pos[0][v] - (width / 2);
					double y = network->pos[1][v] - (height / 2);

					if (x < 0)
						fi = atan(y / x) + PI;
					else if ((x > 0) && (y >= 0))
						fi = atan(y / x);
					else if ((x > 0) && (y < 0))
						fi = atan(y / x) + 2 * PI;
					else if ((x == 0) && (y > 0))
						fi = PI / 2;
					else if ((x == 0) && (y < 0))
						fi = 3 * PI / 2;

					network->pos[0][v] = levelMin[level[v]] * distance * cos(fi) + (width / 2);
					network->pos[1][v] = levelMin[level[v]] * distance * sin(fi) + (height / 2);

					//cout << "inner, x: " << pos[v][0] << " y: " << pos[v][1] << endl;
				}
			}
		}
		//cout << temperature << ", ";
		temperature = temperature * coolFactor;
	}
	/*
	for (i = 0; i < nVertices; i++)
		cout << "level " << i << ": " << level[i] << endl;
	/**/
	//cout << "end coors: " << endl;
	//dumpCoordinates();

	// free space
	for (i = 0; i < nVertices; i++)
	{
		free(disp[i]);
		disp[i] = NULL;
	}
	//cout << endl;
	free(disp);
	disp = NULL;

	return 0;
}



int TNetworkOptimization::smoothFruchtermanReingold(int steps, int center)
{
	/*
	cout << "nVertices: " << nVertices << endl << endl;
	dumpCoordinates();
	/**/
	double **disp = (double**)malloc(nVertices * sizeof (double));
	int i = 0;
	for (i = 0; i < nVertices; i++)
	{
		disp[i] = (double *)calloc(2, sizeof(double));

		if (disp[i] == NULL)
		{
			cerr << "Couldn't allocate memory (disp[])\n";
			return 1;
		}
	}

	int count = 0;
	double kk = 1;
	double localTemparature = 5;
	double area = width * height;

	k2 = area / nVertices;
	k = sqrt(k2);
	kk = 2 * k;
	double kk2 = kk * kk;

	// iterations
	for (i = 0; i < steps; i++)
	{
		//cout << "iteration: " << i << endl;
		// reset disp
		int j = 0;
		for (j = 0; j < nVertices; j++)
		{
			disp[j][0] = 0;
			disp[j][1] = 0;
		}

		int v = 0;
		// calculate repulsive force
		//cout << "repulsive" << endl;
		for (v = 0; v < nVertices - 1; v++)
		{
			for (int u = v + 1; u < nVertices; u++)
			{
				if (level[u] == level[v])
					if (level[u] == 0)
						k = kVector[0];
					else
						k = kVector[1];
				else
					k = kVector[2];

				k2 = k * k;
				kk2 = 4 * k2;

				double difX = network->pos[0][v] - network->pos[0][u];
				double difY = network->pos[1][v] - network->pos[1][u];

				double dif2 = difX * difX + difY * difY;

				if (dif2 < kk2)
				{
					if (dif2 == 0)
						dif2 = 1;

					double dX = difX * k2 / dif2;
					double dY = difY * k2 / dif2;

					disp[v][0] = disp[v][0] + dX;
					disp[v][1] = disp[v][1] + dY;

					disp[u][0] = disp[u][0] - dX;
					disp[u][1] = disp[u][1] - dY;
				}
			}
		}
		// calculate attractive forces
		//cout << "attractive" << endl;
		for (j = 0; j < nLinks; j++)
		{
			int v = links[0][j];
			int u = links[1][j];

			if (level[u] == level[v])
				if (level[u] == 0)
					k = kVector[0];
				else
					k = kVector[1];
			else
				k = kVector[2];

			k2 = k * k;
			kk = 2 * k;

			double difX = network->pos[0][v] - network->pos[0][u];
			double difY = network->pos[1][v] - network->pos[1][u];

			double dif = sqrt(difX * difX + difY * difY);

			double dX = difX * dif / k;
			double dY = difY * dif / k;

			disp[v][0] = disp[v][0] - dX;
			disp[v][1] = disp[v][1] - dY;

			disp[u][0] = disp[u][0] + dX;
			disp[u][1] = disp[u][1] + dY;
		}
		//cout << "limit" << endl;
		// limit the maximum displacement to the temperature t
		// and then prevent from being displaced outside frame
		for (v = 0; v < nVertices; v++)
		{
			double dif = sqrt(disp[v][0] * disp[v][0] + disp[v][1] * disp[v][1]);

			if (dif == 0)
				dif = 1;

			if (v != center)
			{
				network->pos[0][v] = network->pos[0][v] + (disp[v][0] * min(fabs(disp[v][0]), temperature) / dif);
				network->pos[1][v] = network->pos[1][v] + (disp[v][1] * min(fabs(disp[v][1]), temperature) / dif);
			}
		}
		//cout << temperature << ", ";
		temperature = temperature * coolFactor;
	}

	//cout << "end coors: " << endl;
	//dumpCoordinates();

	// free space
	for (i = 0; i < nVertices; i++)
	{
		free(disp[i]);
		disp[i] = NULL;
	}
	//cout << endl;
	free(disp);
	disp = NULL;

	return 0;
}

int TNetworkOptimization::setNetwork(PNetwork net)
{
	network = net;
	//cout << "-1" << endl;
	links[0].clear();
	links[1].clear();

	nVertices = network->nVertices;

	//dumpCoordinates();
	nLinks = 0;
	int v;
	for (v = 0; v < network->nVertices; v++)
	{
		TNetwork::TEdge *edge = network->edges[v];

		if (edge != NULL)
		{
			int u = edge->vertex;

			links[0].push_back(v);
			links[1].push_back(u);
			nLinks++;

			TNetwork::TEdge *next = edge->next;
			while (next != NULL)
			{
				int u = next->vertex;

				links[0].push_back(v);
				links[1].push_back(u);
				nLinks++;

				next = next->next;
			}
		}

    vertices.insert(v);
	}


	//cout << "5" << endl;
	return 0;
}


#include "externs.px"
#include "orange_api.hpp"

PyObject *NetworkOptimization_new(PyTypeObject *type, PyObject *args, PyObject *keyw) BASED_ON (Orange, "(Graph) -> None")
{
  PyTRY
	PyObject *pygraph;

	if (PyArg_ParseTuple(args, "O:NetworkOptimization", &pygraph))
	{
		TGraphAsList *graph = &dynamic_cast<TGraphAsList &>(PyOrange_AsOrange(pygraph).getReference());

		if (graph->nVertices < 2)
		  PYERROR(PyExc_AttributeError, "graph has less than two nodes", NULL);

		//return WrapNewOrange(new TGraphOptimization(graph->nVertices, pos, nLinks, links), type);
		return WrapNewOrange(new TNetworkOptimization(), type);
	}
	else
	{
		return WrapNewOrange(new TNetworkOptimization(), type);
	}
  PyCATCH
}

PyObject *NetworkOptimization_setGraph(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "(Graph) -> None")
{
  PyTRY
  PNetwork net;
	if (!PyArg_ParseTuple(args, "O&:NetworkOptimization.setGraph", cc_Network, &net))
			return NULL;

	CAST_TO(TNetworkOptimization, netOptimization);

	if (netOptimization->setNetwork(net) > 0)
		PYERROR(PyExc_SystemError, "setGraph failed", NULL);

	RETURN_NONE;
  PyCATCH
}

bool hasVertex(int vertex, vector<int> list)
{
	int i;
	for (i = 0; i < list.size(); i++)
	{
		//cout << list[i] << " " << vertex << endl;
		if (list[i] == vertex)
			return true;
	}

	return false;
}

PyObject *NetworkOptimization_random(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "() -> None")
{
  PyTRY
	CAST_TO(TNetworkOptimization, graph);

	graph->random();

	RETURN_NONE;
  PyCATCH
}

PyObject *NetworkOptimization_fruchtermanReingold(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "(steps, temperature, coolFactor, hiddenNodes, weighted) -> temperature")
{
  PyTRY
	int steps;
	double temperature = 0;
	double coolFactor = 0;
	PyObject* hiddenNodes = PyList_New(0);
	bool weighted = false;

	if (!PyArg_ParseTuple(args, "id|dOb:NetworkOptimization.fruchtermanReingold", &steps, &temperature, &coolFactor, &hiddenNodes, &weighted))
		return NULL;

	int size = PyList_Size(hiddenNodes);

	CAST_TO(TNetworkOptimization, graph);

	// remove links for hidden nodes
	vector<int> removedLinks[2];
	int i, j;
	for (i = 0; i < size; i++)
	{
		int node = PyInt_AsLong(PyList_GetItem(hiddenNodes, i));

		//cout <<"size: " << graph->links1->size() << endl;
		for (j = graph->links[0].size() - 1; j >= 0; j--)
		{
			if (graph->links[0][j] == node || graph->links[1][j] == node)
			{
				//cout << "j: " << j << " u: " << graph->links1[0][j] << " v: " << graph->links1[1][j] << endl;
				removedLinks[0].push_back(graph->links[0][j]);
				removedLinks[1].push_back(graph->links[1][j]);

				graph->links[0].erase(graph->links[0].begin() + j);
				graph->links[1].erase(graph->links[1].begin() + j);
			}
		}
	}
	graph->nLinks = graph->links[0].size();

	graph->temperature = temperature;

	if (coolFactor == 0)
		graph->coolFactor = exp(log(10.0/10000.0) / steps);
	else
		graph->coolFactor = coolFactor;

	if (graph->fruchtermanReingold(steps, weighted) > 0)
	{
		PYERROR(PyExc_SystemError, "fruchtermanReingold failed", NULL);
	}

	// adds back removed links
	for (i = 0; i < removedLinks[0].size(); i++)
	{
		graph->links[0].push_back(removedLinks[0][i]);
		graph->links[1].push_back(removedLinks[1][i]);
	}

	graph->nLinks = graph->links[0].size();

	return Py_BuildValue("d", graph->temperature);
  PyCATCH
}

PyObject *NetworkOptimization_radialFruchtermanReingold(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "(center, steps, temperature) -> temperature")
{
  PyTRY

	int steps, center;
	double temperature = 0;

	if (!PyArg_ParseTuple(args, "iid:NetworkOptimization.radialFruchtermanReingold", &center, &steps, &temperature))
		return NULL;

	CAST_TO(TNetworkOptimization, graph);

	graph->network->pos[0][center] = graph->width / 2;
	graph->network->pos[1][center] = graph->height / 2;

	int nCircles = 6;
	int r = graph->width / nCircles / 2;

	graph->level = new int[graph->nVertices];
	graph->kVector = new double[nCircles];
	graph->levelMin = new double[nCircles];
	graph->levelMax = new double[nCircles];
	int i;
	for (i = 0; i < graph->nVertices; i++)
		graph->level[i] = nCircles;

	for (i = 0; i < nCircles; i++)
	{
		graph->kVector[i] = 0;
		graph->levelMin[i] = INT_MAX;
		graph->levelMax[i] = 0;
	}
	vector<int> removedLinks[2];
	vector<int> vertices;
	vector<int> allVertices;
	vertices.push_back(center);
	graph->level[center] = 0;

	for (i = 0; i < nCircles; i++)
	{
		// position vertices
		double fi = 360 / vertices.size();
		int v;
		for (v = 0; v < vertices.size(); v++)
		{
			double x = i * r * cos(v * fi * PI / 180) + (graph->width / 2);
			double y = i * r * sin(v * fi * PI / 180) + (graph->height / 2);

			graph->network->pos[0][vertices[v]] = x;
			graph->network->pos[1][vertices[v]] = y;

			//cout << "v: " << vertices[v] << " X: " << x << " Y: " << y << " level: " << graph->level[vertices[v]] << endl;
		}
		//cout << endl;
		vector<int> newVertices;
		for (v = 0; v < vertices.size(); v++)
		{
			int j;
			int node = vertices[v];

			for (j = graph->links[0].size() - 1; j >= 0; j--)
			{
				if (graph->links[0][j] == node)
				{
					//cout << "j: " << j << " u: " << graph->links1[0][j] << " v: " << graph->links1[1][j] << endl;
					removedLinks[0].push_back(graph->links[0][j]);
					removedLinks[1].push_back(graph->links[1][j]);

					if (!hasVertex(graph->links[1][j], allVertices))
					{
						newVertices.push_back(graph->links[1][j]);
						allVertices.push_back(graph->links[1][j]);
						graph->level[graph->links[1][j]] = i + 1;
					}
					graph->links[0].erase(graph->links[0].begin() + j);
					graph->links[1].erase(graph->links[1].begin() + j);
				}
				else if (graph->links[1][j] == node)
				{
					//cout << "j: " << j << " u: " << graph->links1[0][j] << " v: " << graph->links1[1][j] << endl;
					removedLinks[0].push_back(graph->links[0][j]);
					removedLinks[1].push_back(graph->links[1][j]);

					if (!hasVertex(graph->links[0][j], allVertices))
					{
						//cout << "adding: " <<
						newVertices.push_back(graph->links[0][j]);
						allVertices.push_back(graph->links[0][j]);
						graph->level[graph->links[0][j]] = i + 1;
					}

					graph->links[0].erase(graph->links[0].begin() + j);
					graph->links[1].erase(graph->links[1].begin() + j);
				}
			}
		}

		vertices.clear();

		if (newVertices.size() == 0)
			break;

		for (v = 0; v < newVertices.size(); v++)
		{
			vertices.push_back(newVertices[v]);
		}
	}
	// adds back removed links
	for (i = 0; i < removedLinks[0].size(); i++)
	{
		graph->links[0].push_back(removedLinks[0][i]);
		graph->links[1].push_back(removedLinks[1][i]);
	}


	for (i = 0; i < graph->nVertices; i++)
	{
		if (graph->level[i] >= nCircles)
			graph->level[i] = nCircles - 1;

		graph->kVector[graph->level[i]]++;
	}

	double radius = graph->width / nCircles / 2;
	for (i = 0; i < nCircles; i++)
	{
		//cout << "n: " << graph->kVector[i] << endl;
		//cout << "r: " << radius * i;
		if (graph->kVector[i] > 0)
			graph->kVector[i] = 2 * i * radius * sin(PI / graph->kVector[i]);
		else
			graph->kVector[i] = -1;

		//cout << "kvec: " << graph->kVector[i] << endl;
	}

	graph->temperature = temperature;
	graph->coolFactor = exp(log(10.0/10000.0) / steps);
	/*
	for (i = 0; i < graph->nVertices; i++)
		cout << "level " << i << ": " << graph->level[i] << endl;
	/**/
	if (graph->radialFruchtermanReingold(steps, nCircles) > 0)
	{
		delete[] graph->level;
		delete[] graph->kVector;
		delete[] graph->levelMin;
		delete[] graph->levelMax;
		PYERROR(PyExc_SystemError, "radialFruchtermanReingold failed", NULL);
	}

	delete[] graph->level;
	delete[] graph->kVector;
	delete[] graph->levelMin;
	delete[] graph->levelMax;
	return Py_BuildValue("d", graph->temperature);
  PyCATCH
}



PyObject *NetworkOptimization_smoothFruchtermanReingold(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "(center, steps, temperature, coolFactor) -> temperature")
{
  PyTRY
	int steps, center;
	double temperature = 0;
	double coolFactor = 0;
	if (!PyArg_ParseTuple(args, "iid|d:NetworkOptimization.smoothFruchtermanReingold", &center, &steps, &temperature, &coolFactor))
		return NULL;

	CAST_TO(TNetworkOptimization, graph);

	if (coolFactor == 0)
		graph->coolFactor = exp(log(10.0/10000.0) / steps);
	else
		graph->coolFactor = coolFactor;

	graph->level = new int[graph->nVertices];
	graph->kVector = new double[3];

	int i;
	for (i = 0; i < graph->nVertices; i++)
		graph->level[i] = 1;

	vector<int> neighbours;
	graph->network->getNeighbours(center, neighbours);
	int nNeighbours = neighbours.size();

	ITERATE(vector<int>, ni, neighbours)
	{
		graph->level[*ni] = 0;
	}

	graph->level[center] = 0;

	double area = graph->width * graph->height;
	double k2 = area / graph->nVertices;

	graph->kVector[0] = sqrt(PI * 9 * k2 / nNeighbours) / 2;
	graph->kVector[1] = sqrt(k2);
	graph->kVector[2] = 3 * sqrt(k2);


	graph->temperature = temperature;

	if (graph->smoothFruchtermanReingold(steps, center) > 0)
	{
		delete[] graph->level;
		delete[] graph->kVector;
		PYERROR(PyExc_SystemError, "smoothFruchtermanReingold failed", NULL);
	}

	delete[] graph->level;
	delete[] graph->kVector;
	return Py_BuildValue("d", graph->temperature);
  PyCATCH
}



PyObject *NetworkOptimization_circularOriginal(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "() -> None")
{
  PyTRY
	CAST_TO(TNetworkOptimization, graph);
	graph->circular(0);
	RETURN_NONE;
  PyCATCH
}

PyObject *NetworkOptimization_circularRandom(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "() -> None")
{
  PyTRY
	CAST_TO(TNetworkOptimization, graph);
	graph->circular(1);
	RETURN_NONE;
  PyCATCH
}


PyObject *NetworkOptimization_circularCrossingReduction(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "() -> None")
{
  PyTRY
	CAST_TO(TNetworkOptimization, graph);
	graph->circularCrossingReduction();
	RETURN_NONE;
  PyCATCH
}

int *getVertexPowers(TNetworkOptimization *graph)
{
	int *vertexPower = new int[graph->nVertices];

	int i;
	for (i=0; i < graph->nVertices; i++)
	{
		vertexPower[i] = 0;
	}

	for (i=0; i < graph->nLinks; i++)
	{
		vertexPower[graph->links[0][i]]++;
		vertexPower[graph->links[1][i]]++;
	}

  return vertexPower;
}

PyObject *NetworkOptimization_getVertexPowers(PyObject *self, PyObject *) PYARGS(METH_NOARGS, "() -> list")
{
  PyTRY
    CAST_TO(TNetworkOptimization, graph);
    int *vertexPower = getVertexPowers(graph);
    PyObject *pypowers = PyList_New(graph->nVertices);
    for(int i =0; i < graph->nVertices; i++)
      PyList_SetItem(pypowers, i, PyInt_FromLong(vertexPower[i]));
    delete [] vertexPower;
    return pypowers;
  PyCATCH;
}

PyObject *NetworkOptimization_closestVertex(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "(x, y) -> Ndx")
{
  PyTRY
	double x;
	double y;

	if (!PyArg_ParseTuple(args, "dd:NetworkOptimization.closestVertex", &x, &y))
		return NULL;

	CAST_TO(TNetworkOptimization, graph);

	int i;
	double min = 100000000;
	int ndx = -1;
	for (i=0; i < graph->nVertices; i++)
	{
		double dX = graph->network->pos[0][i] - x;
		double dY = graph->network->pos[1][i] - y;
		double d = dX*dX + dY*dY;

		if (d < min)
		{
			min = d;
			ndx = i;
		}
	}

	return Py_BuildValue("id", ndx, sqrt(min));
  PyCATCH
}

PyObject *NetworkOptimization_vertexDistances(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "(x, y) -> List of (distance, vertex)")
{
  PyTRY
	double x;
	double y;

	if (!PyArg_ParseTuple(args, "dd:NetworkOptimization.vertexDistances", &x, &y))
		return NULL;

	CAST_TO(TNetworkOptimization, graph);

	int i;
	PyObject* distancies = PyList_New(0);
	for (i=0; i < graph->nVertices; i++)
	{
		double dX = graph->network->pos[0][i] - x;
		double dY = graph->network->pos[1][i] - y;
		double d = dX*dX + dY*dY;

		PyObject *nel = Py_BuildValue("di", d, i);
		PyList_Append(distancies, nel);
		Py_DECREF(nel);
	}

	return distancies;
  PyCATCH
}

PyObject *NetworkOptimization_getVerticesInRect(PyObject *self, PyObject *args) PYARGS(METH_VARARGS, "(x1, y1, x2, y2) -> list of vertices")
{
  PyTRY
	double x1, y1, x2, y2;

	if (!PyArg_ParseTuple(args, "dddd:NetworkOptimization.getVerticesInRect", &x1, &y1, &x2, &y2))
		return NULL;

	if (x1 > x2) {
		double tmp = x2;
		x2 = x1;
		x1 = tmp;
	}

	if (y1 > y2) {
		double tmp = y2;
		y2 = y1;
		y1 = tmp;
	}

	CAST_TO(TNetworkOptimization, graph);
	PyObject* vertices = PyList_New(0);
	int i;
	for (i = 0; i < graph->nVertices; i++) {
		double vX = graph->network->pos[0][i];
		double vY = graph->network->pos[1][i];

		if ((x1 <= vX) && (x2 >= vX) && (y1 <= vY) && (y2 >= vY)) {
			PyObject *nel = Py_BuildValue("i", i);
			PyList_Append(vertices, nel);
			Py_DECREF(nel);
		}
	}

	return vertices;
  PyCATCH
}

#include "networkoptimization.px"
