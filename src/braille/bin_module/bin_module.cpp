#include <Python.h>
#include <algorithm>


extern "C" void bradley_binarization(PyObject *pixels, PyObject *width, PyObject *height, PyObject *bradley_param){
    long w = PyLong_AsLong(width);
    long h = PyLong_AsLong(height);
    long bradley_p = PyLong_AsLong(bradley_param);

    bradley_p = std::clamp(bradley_p, 1L, 32L);
    
    const int S = w / bradley_p;
    int s2 = S / 2;
    const float t = 0.15;
    unsigned long* integral_image = (unsigned long*)malloc(sizeof(unsigned long) * w * h);
    long sum = 0;
    int count = 0;
    int index;
    int x1, y1, x2, y2;


    for (int x = 0; x < w; x++){
        sum = 0;
        for (int y = 0; y < h; y++){
            index = y * w + x;
            sum += PyLong_AsLong(PyList_GetItem(pixels, index));
            if (x == 0)
                integral_image[index] = sum;
            else
                integral_image[index] = integral_image[index - 1] + sum;
        }
    }

    for (int x = 0; x < w; ++x) {
        for (int y = 0; y < h; ++y) {
            index = y * w + x;

            x1 = x - s2;
            x2 = x + s2;
            y1 = y - s2;
            y2 = y + s2;

            if (x1 < 0)
                x1 = 0;
            if (x2 >= w)
                x2 = w - 1;
            if (y1 < 0)
                y1 = 0;
            if (y2 >= h)
                y2 = h - 1;

            count = (x2 - x1) * (y2 - y1);

            sum = integral_image[y2 * w + x2] - integral_image[y1 * w + x2] -
                integral_image[y2 * w + x1] + integral_image[y1 * w + x1];
            
            long p = PyLong_AsLong(PyList_GetItem(pixels, index));
            if ((p * count) < (long)(sum * (1.0 - t)))
                PyList_SetItem(pixels, index, PyLong_FromLong(0));
            else
                PyList_SetItem(pixels, index, PyLong_FromLong(255));
        }
    }
}


extern "C" void anti_aliasing(PyObject *pixels, PyObject *width, PyObject *height, PyObject *intensity)
{
    long intens = PyLong_AsLong(intensity);
    long h = PyLong_AsLong(height);
    long w = PyLong_AsLong(width);

    for (int i = 0; i <= intens; i++)
        for (int y = 1; y < h-1; y++)
            for (int x = 1; x < w-1; x++)
            {
                long p = PyLong_AsLong(PyList_GetItem(pixels, y * w + x));
                long p1 = PyLong_AsLong(PyList_GetItem(pixels, y * w + x-1));
                long p2 = PyLong_AsLong(PyList_GetItem(pixels, y * w + x+1));
                long p3 = PyLong_AsLong(PyList_GetItem(pixels, y * w + x - w));
                long p4 = PyLong_AsLong(PyList_GetItem(pixels, y * w + x + w));
                p = (p + p1 + p2 + p3 + p4) / 5;
                PyList_SetItem(pixels, y * w + x, PyLong_FromLong(p));
            }
}
