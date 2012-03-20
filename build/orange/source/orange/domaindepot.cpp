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

#include "vars.hpp"
#include "domain.hpp"
#include "getarg.hpp"

#include "stringvars.hpp"

#include "domaindepot.hpp"


TDomainDepot domainDepot;

extern TOrangeType PyOrVariable_Type;
extern TOrangeType PyOrPythonVariable_Type;
#include "pythonvars.hpp"
#include "c2py.hpp"

typedef vector<pair<string, PyObject *> > TPythonVariablesRegistry;

TPythonVariablesRegistry pythonVariables;

void registerVariableType(PyObject *variable)
{
  const char *varname;

  if (!PyType_IsSubtype((PyTypeObject *)variable, (PyTypeObject *)&PyOrPythonVariable_Type))
    raiseErrorWho("registerVariableType", "variable type must be derived from PythonVariable");

  PyObject *pyclassname = PyObject_GetAttrString(variable, "__name__");
  if (!pyclassname)
    raiseErrorWho("registerVariableType", "variable type misses the '__name__'");
  varname = PyString_AsString(pyclassname);

  TPythonVariablesRegistry::iterator bi(pythonVariables.begin()), be(pythonVariables.end());
  for(; (bi != be) && ((*bi).first != varname); bi++);

  Py_INCREF(variable);
  if (bi==be)
    pythonVariables.push_back(make_pair(string(varname), variable));
  else {
    Py_DECREF((*bi).second);
    (*bi).second = variable;
  }

  Py_DECREF(pyclassname);
}

void pythonVariables_unsafeInitializion()
{
  pythonVariables.push_back(make_pair(string("PythonVariable"), (PyObject *)&PyOrPythonVariable_Type));
}

bool pythonDeclarationMatches(const string &declaration, PVariable var)
{
  PyObject *classname = PyObject_GetAttrString((PyObject *)(var.counter), "__class__");
  PyObject *typenamee = PyObject_GetAttrString(classname, "__name__");
  bool res = !strcmp(PyString_AsString(typenamee), (declaration.size()>6) ? declaration.c_str()+7 : "PythonVariable");
  Py_DECREF(classname);
  Py_DECREF(typenamee);
  return res;
}



PDomain combineDomains(PDomainList sources, TDomainMultiMapping &mapping)
{
  PVariable classVar;
  // I would use reverse iterators, but don't have them
  TDomainList::const_iterator cri(sources->end()), cre(sources->begin());
  while(!(*--cri)->classVar && (cri!=cre));
  classVar = (*cri)->classVar; // might have stopped at the classvar and reached cre which has none...
      
  TVarList variables;

  mapping.clear();
  vector<pair<int, int> > classMapping;

  int domainIdx = 0;
  TDomainList::const_iterator di(sources->begin()), de(sources->end());
  for(; di!=de; di++, domainIdx++) {

    int varIdx = 0;
    TVarList::const_iterator vi((*di)->variables->begin()), ve((*di)->variables->end());
    for(; vi!=ve; vi++, varIdx++) {
      if (*vi == classVar)
        classMapping.push_back(make_pair(domainIdx, varIdx));
      else {
        TDomainMultiMapping::iterator dmmi(mapping.begin());
        TVarList::const_iterator hvi(variables.begin()), hve(variables.end());
        for(; (hvi!=hve) && (*hvi != *vi); hvi++, dmmi++);
        if (hvi==hve) {
          variables.push_back(*vi);
          mapping.push_back(vector<pair<int, int> >());
          mapping.back().push_back(make_pair(domainIdx, varIdx));
        }
        else
          (*dmmi).push_back(make_pair(domainIdx, varIdx));
      }
    }
  }

  if (classVar)
    mapping.push_back(classMapping);

  TDomain *newDomain = mlnew TDomain(classVar, variables);
  PDomain wdomain = newDomain;

  for(domainIdx = 0, di = sources->begin(); di!=de; domainIdx++, di++)
    const_ITERATE(TMetaVector, mi, (*di)->metas) {
      PVariable metavar = newDomain->getMetaVar((*mi).id, false);
      if (!metavar)
        newDomain->metas.push_back(*mi);
      else
        if (metavar != (*mi).variable)
          raiseError("Id %i represents two different attributes ('%s' and '%s')", (*mi).id, metavar->get_name().c_str(), (*mi).variable->get_name().c_str());
    }

  return wdomain;
}


void computeMapping(PDomain destination, PDomainList sources, TDomainMultiMapping &mapping)
{
  mapping.clear();
  const_PITERATE(TVarList, vi, destination->variables) {
    mapping.push_back(vector<pair<int, int> >());
    int domainIdx = 0;
    TDomainList::const_iterator si(sources->begin()), se(sources->end());
    for(; si!=se; si++, domainIdx++) {
      int pos = (*si)->getVarNum(*vi, false);
      if (pos != ILLEGAL_INT)
        mapping.back().push_back(make_pair(domainIdx, pos));
    }
  }
}



TDomainDepot::TAttributeDescription::TAttributeDescription(const string &n, const int &vt, const string &td, bool ord)
: name(n),
  varType(vt),
  typeDeclaration(td),
  ordered(ord)
{}


TDomainDepot::TAttributeDescription::TAttributeDescription(const string &n, const int &vt)
: name(n),
  varType(vt),
  typeDeclaration(),
  ordered(false)
{}


TDomainDepot::TAttributeDescription::TAttributeDescription(PVariable pvar)
: preparedVar(pvar)
{}


void TDomainDepot::TAttributeDescription::addValue(const string &s)
{
  fixedOrderValues.push_back(s);
  values[s] = 1;
}

TDomainDepot::~TDomainDepot()
{
  ITERATE(list<TDomain *>, di, knownDomains) {
    // this could be done by some remove_if, but I don't want to fight
    //   all various implementations of STL
    list<TDomain::TDestroyNotification>::iterator src((*di)->destroyNotifiers.begin()), end((*di)->destroyNotifiers.end());
    for(; (src!=end) && ((const TDomainDepot *)((*src).second) != this); src++);
    (*di)->destroyNotifiers.erase(src);
  }
}


void TDomainDepot::destroyNotifier(TDomain *domain, void *data)
{ 
  ((TDomainDepot *)(data))->knownDomains.remove(domain);
}


 
inline bool checkValueOrder(PVariable var, const TDomainDepot::TAttributeDescription &desc)
{
  return    desc.varType != TValue::INTVAR
         || dynamic_cast<TEnumVariable &>(var.getReference()).checkValuesOrder(desc.fixedOrderValues);
}

void augmentVariableValues(PVariable var, const TDomainDepot::TAttributeDescription &desc)
{
  if (desc.varType != TValue::INTVAR)
    return;
    
  TEnumVariable &evar = dynamic_cast<TEnumVariable &>(var.getReference());
  const_ITERATE(TStringList, fvi, desc.fixedOrderValues)
    evar.addValue(*fvi);
  vector<string> sorted;
  set<string> values;
  for(map<string, int>::const_iterator dvi(desc.values.begin()), dve(desc.values.end()); dvi != dve; dvi++)
    values.insert(values.end(), dvi->first);
  TEnumVariable::presortValues(values, sorted);
  const_ITERATE(vector<string>, ssi, sorted)
    evar.addValue(*ssi);
}


bool TDomainDepot::checkDomain(const TDomain *domain, 
                               const TPAttributeDescriptions *attributes, bool hasClass,
                               const TPAttributeDescriptions *metas,
                               int *metaIDs)
{
  // check the number of attributes and meta attributes, and the presence of class attribute
  if (    (domain->variables->size() != attributes->size())
       || (bool(domain->classVar) != hasClass)
       || (metas ? (metas->size() != domain->metas.size()) : domain->metas.size() )
     )
    return false;

  // check the names and types of attributes
  TVarList::const_iterator vi(domain->variables->begin());
  TPAttributeDescriptions::const_iterator ai(attributes->begin()), ae(attributes->end());
  for(; ai != ae; ai++, vi++)
    if (    ((**ai).name != (*vi)->get_name())
         || ((**ai).varType>0) && ((**ai).varType != (*vi)->varType)
         || (((**ai).varType==PYTHONVAR) && !pythonDeclarationMatches((**ai).typeDeclaration, *vi))
         || !checkValueOrder(*vi, **ai)
       )
      return false;

  // check the meta attributes if they exist
  TPAttributeDescriptions::const_iterator mi, me;
  if (metas) {
    for(mi = metas->begin(), me = metas->end(); mi != me; mi++) {
      PVariable var = domain->getMetaVar((**mi).name, false);
      if (    !var
           || (((**mi).varType > 0) && ((**mi).varType != var->varType))
           || (((**mi).varType==PYTHONVAR) && !pythonDeclarationMatches((**mi).typeDeclaration, var))
           || !checkValueOrder(var, **mi)
         )
        return false;
      if (metaIDs)
        *(metaIDs++) = domain->getMetaNum((**mi).name, false);
    }
  }

  for(ai = attributes->begin(), vi = domain->variables->begin(); ai != ae; ai++, vi++)
    augmentVariableValues(*vi, **ai);
  for(mi = metas->begin(); mi != me; mi++)
    if ((**mi).varType == TValue::INTVAR)
      augmentVariableValues(domain->getMetaVar((**mi).name), **mi);
      
  return true;
}


PDomain TDomainDepot::prepareDomain(TPAttributeDescriptions *attributes, bool hasClass,
                                    TPAttributeDescriptions *classDescriptions,
                                    TPAttributeDescriptions *metas, const int createNewOn,
                                    vector<int> &status, vector<pair<int, int> > &metaStatus)
{ 
  int tStatus;

  status.clear();
  TVarList attrList;
  PITERATE(TPAttributeDescriptions, ai, attributes) {
    attrList.push_back(makeVariable(**ai, tStatus, createNewOn));
    status.push_back(tStatus);
  }
  
  PDomain newDomain;
  PVariable classVar;
  if (hasClass) {
    classVar = attrList.back();
    attrList.erase(attrList.end()-1);
  }
  
  newDomain = mlnew TDomain(classVar, attrList);

  if (classDescriptions) {
      PITERATE(TPAttributeDescriptions, ai, classDescriptions) {
          newDomain->classVars->push_back(makeVariable(**ai, tStatus, createNewOn));
      }
  }

  metaStatus.clear();
  if (metas)
    PITERATE(TPAttributeDescriptions, mi, metas) {
      PVariable var = makeVariable(**mi, tStatus, createNewOn);
      int id = var->defaultMetaId;
      if (!id)
        id = getMetaID();
      newDomain->metas.push_back(TMetaDescriptor(id, var));
      metaStatus.push_back(make_pair(id, tStatus));
    }
    
  return newDomain;
}

PVariable TDomainDepot::createVariable_Python(const string &typeDeclaration, const string &name)
{
  if (typeDeclaration.size() == 6) {
    TPythonVariable *var = mlnew TPythonVariable();
    var->set_name(name);
    return var;
  }


  char *vartypename = const_cast<char *>(typeDeclaration.c_str()+7);
  char *parpos = strchr(vartypename, '(');
  PyObject *var = NULL;

  if (!parpos) {
    TPythonVariablesRegistry::iterator bi(pythonVariables.begin()), be(pythonVariables.end());
    for(; (bi != be) && strcmp((*bi).first.c_str(), vartypename); bi++);

    if (bi!=be) {
      var = PyObject_CallFunction((*bi).second, NULL);
      if (!var)
        throw pyexception();
    }
  }

  if (!var) {
    PyObject *globals = PyEval_GetGlobals();
    PyObject *locals = PyEval_GetLocals();

    var = PyRun_String(vartypename, Py_eval_input, globals, locals);
    if (!parpos && (!var || PyType_Check(var))) {
      PyErr_Clear();
      const int slen = strlen(vartypename);
      char *wPar = strcpy(new char [slen + 3], vartypename);
      strcpy(wPar+slen, "()");
      var = PyRun_String(wPar, Py_eval_input, globals, locals);
    }
  
    if (!var)
      // if parentheses were given, this is the exception from the first call, else from the second
      throw pyexception();
  }

  if (!PyObject_TypeCheck(var, (PyTypeObject *)&PyOrVariable_Type)) {
    Py_DECREF(var);
    ::raiseErrorWho("make_variable", "PythonVariable's constructor is expected to return a 'PythonVariable', not '%s'", var->ob_type->tp_name);
  }

  PVariable pvar = GCPtr<TOrange>((TPyOrange *)var, true);
  Py_DECREF(var);

  pvar->set_name(name);
  return pvar;
}


int Orange_setattrDictionary(TPyOrange *self, const char *name, PyObject *args, bool warn);

PVariable TDomainDepot::makeVariable(TAttributeDescription &desc, int &status, const int &createNewOn)
{
  set<string> values;
  for(map<string, int>::const_iterator dvi(desc.values.begin()), dve(desc.values.end()); dvi != dve; dvi++)
    values.insert(values.end(), dvi->first);
    
  PVariable var = TVariable::make(desc.name, desc.varType, &desc.fixedOrderValues, &values, createNewOn, &status);
  
  if (!var) {
    if (desc.varType == PYTHONVAR) {
      var = createVariable_Python(desc.typeDeclaration, desc.name);
      status = TVariable::NotFound;
    }

    if (!var)
      ::raiseErrorWho("make_variable", "unknown type for attribute '%s'", desc.name.c_str());
  }
  
  if (var && desc.ordered)
    var->ordered = true;
    
  if (desc.userFlags.size()) {
    PyObject *attrdict = PyDict_New();
    ITERATE(TMultiStringParameters, si, desc.userFlags) {
      PyObject *value = PyString_FromString((*si).second.c_str());
      PyDict_SetItemString(attrdict, (*si).first.c_str(), value);
      Py_DECREF(value);
    }
      
    Orange_setattrDictionary((TPyOrange *)(var.counter), "attributes", attrdict, false);
    Py_DECREF(attrdict);
    PyErr_Clear();
  }
  
  return var;
}


void TDomainDepot::pattrFromtAttr(TDomainDepot::TAttributeDescriptions &descs, TDomainDepot::TPAttributeDescriptions &pdescs) {
  pdescs.clear();
  ITERATE(TDomainDepot::TAttributeDescriptions, adi, descs) {
    pdescs.push_back(&*adi);
  }
}


