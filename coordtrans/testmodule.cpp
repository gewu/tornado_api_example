/***************************************************************************
 * 
 * Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
 * 
 **************************************************************************/
 
 
 
/**
 * @file testmodule.c
 * @author gewu(com@baidu.com)
 * @date 2015/05/18 19:19:19
 * @brief 
 *  
 **/

#include "coordtrans.cpp"

static PyObject* wrap_coordtrans(PyObject* self, PyObject *args){

    char *from = "gcj02ll"
    char *to = "bd09ll"
    
    float x, y;
    float rx, ry;

    PyObject *ret1;
    PyObject *ret2;
    PyObject *list = NULL;


    if (!PyArg_ParseTuple(args, "ff", &x, &y))
        return NULL

    coordtrans(from, to, &x, &y, &rx, &ry)
    
    ret1 = Py_BuildValue("f", &rx)
    ret2 = Py_BuildValue("f", &ry)

    PyList_SetItem(list, 0, ret1)
    PyList_setItem(list, 1, ret2)

    return list;
}

static PyMethodDef ModuleMethods[] = 
{
    {"coordtrans", wrap_coordtrans, METH_VARARGS, "tran the geom"}
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC

inittestmodule(void){
    (void)Py_InitModule("testmodule", ModuleMethod);
}

















/* vim: set expandtab ts=4 sw=4 sts=4 tw=100: */
