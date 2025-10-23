# PRACTICA-1
usage: colab_kernel_launcher.py [-h] --tickers TICKERS --inicio INICIO --fin
                                FIN [--guardar]
colab_kernel_launcher.py: error: the following arguments are required: --tickers, --inicio, --fin
ERROR:root:Internal Python error in the inspect module.
Below is the traceback from this internal error.

Traceback (most recent call last):
  File "/usr/lib/python3.12/argparse.py", line 1943, in _parse_known_args2
    namespace, args = self._parse_known_args(args, namespace, intermixed)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/argparse.py", line 2230, in _parse_known_args
    raise ArgumentError(None, _('the following arguments are required: %s') %
argparse.ArgumentError: the following arguments are required: --tickers, --inicio, --fin

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.12/dist-packages/IPython/core/interactiveshell.py", line 3553, in run_code
    exec(code_obj, self.user_global_ns, self.user_ns)
  File "/tmp/ipython-input-3070867861.py", line 53, in <cell line: 0>
    main()
  File "/tmp/ipython-input-3070867861.py", line 43, in main
    args = parser.parse_args()
           ^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/argparse.py", line 1904, in parse_args
    args, argv = self.parse_known_args(args, namespace)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/argparse.py", line 1914, in parse_known_args
    return self._parse_known_args2(args, namespace, intermixed=False)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/argparse.py", line 1945, in _parse_known_args2
    self.error(str(err))
  File "/usr/lib/python3.12/argparse.py", line 2650, in error
    self.exit(2, _('%(prog)s: error: %(message)s\n') % args)
  File "/usr/lib/python3.12/argparse.py", line 2637, in exit
    _sys.exit(status)
SystemExit: 2

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.12/dist-packages/IPython/core/ultratb.py", line 1101, in get_records
    return _fixed_getinnerframes(etb, number_of_lines_of_context, tb_offset)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/IPython/core/ultratb.py", line 248, in wrapped
    return f(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/IPython/core/ultratb.py", line 281, in _fixed_getinnerframes
    records = fix_frame_records_filenames(inspect.getinnerframes(etb, context))
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/inspect.py", line 1769, in getinnerframes
    traceback_info = getframeinfo(tb, context)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/inspect.py", line 1701, in getframeinfo
    lineno = frame.f_lineno
             ^^^^^^^^^^^^^^
AttributeError: 'tuple' object has no attribute 'f_lineno'
---------------------------------------------------------------------------
ArgumentError                             Traceback (most recent call last)
/usr/lib/python3.12/argparse.py in _parse_known_args2(self, args, namespace, intermixed)
   1942             try:
-> 1943                 namespace, args = self._parse_known_args(args, namespace, intermixed)
   1944             except ArgumentError as err:

15 frames
ArgumentError: the following arguments are required: --tickers, --inicio, --fin

During handling of the above exception, another exception occurred:

SystemExit                                Traceback (most recent call last)
    [... skipping hidden 1 frame]

SystemExit: 2

During handling of the above exception, another exception occurred:

TypeError                                 Traceback (most recent call last)
    [... skipping hidden 1 frame]

/usr/local/lib/python3.12/dist-packages/IPython/core/ultratb.py in find_recursion(etype, value, records)
    380     # first frame (from in to out) that looks different.
    381     if not is_recursion_error(etype, value, records):
--> 382         return len(records), 0
    383 
    384     # Select filename, lineno, func_name to track frames with

TypeError: object of type 'NoneType' has no len()
