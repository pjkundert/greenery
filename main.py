# This code is in the public domain.

# http://qntm.org/greenery

from __future__ import print_function

# Allow import of package from executable within its directory
import sys, os
sys.path.insert( 0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import greenery

regexes = []
verbose = 0
interactive = 0
errors = 0
helptext = 0
timing = 0
tests = None

# Extract options:
#    --verbose,	    -v[vv]
#    --interactive, -i
#    --help,        -h
#    --time,        -t
#    -- "test string" ...

for i in range(1,len(sys.argv)):
	arg = sys.argv[i]
	# Long-form options "--word"?
	if arg == "--verbose":
		arg="-v"
	elif arg == "--interactive":
		arg="-i"
	elif arg == "--help":
		arg="-h"
	elif arg == "--time":
		arg="-t"
	elif arg == "--":
                #  -- ...: Remaining args are test vectors
		tests = sys.argv[i+1:]
		break
	elif arg.startswith("--"):
		print("Unrecognized long option: %s" % ( arg ))
		exit(1)
	elif not arg.startswith("-"):
		regexes.append(arg)
		continue
	# Short-form options "-x[...]"
	for opt in arg[1:]:
		if opt == "h":
			helptext += 1
		elif opt == "v":
			verbose += 1
		elif opt == "i":
			interactive += 1
		elif opt == "t":
			timing += 1
		else:
			print("Invalid option: -%s" % ( opt ))
			errors += 1
if len(regexes) < 1:
	print("Please supply several regexes to compute their intersection, union and concatenation.")
	print("E.g. \"19.*\" \"\\d{4}-\\d{2}-\\d{2}\"")
	errors += 1

if errors or helptext:
	print("%s [--verbose|-v] [--help|-h] [--interactive|-i] [--time|-t] regex [...] [-- test ...]" % ( sys.argv[0] ))

if errors:
	exit(1)

def build( regexes ):
	# Builds a dictionary of "Label": (lego,fsm) for Concatenation,
	# Intersection and Union, including all supplied regular expressions.
	d = dict()

	i = greenery.parse(regexes[0])
	for regex in regexes[1:]:
		i &= greenery.parse(regex)
	d["Intersection"] = (i,i.fsm())

	u = greenery.parse(regexes[0])
	for regex in regexes[1:]:
		u |= greenery.parse(regex)
	ufsm = d["Union"] = (u,u.fsm())
	
	c = greenery.parse(regexes[0])
	for regex in regexes[1:]:
		c += greenery.parse(regex)
	cfsm = d["Concatenation"] = (c,c.fsm())

	return d

if timing:
	# Compute the cost to parse the regular expression (lego), and build the
	# finite state machine (fsm) for all the compositions of the given
	# regular expressions.
	import timeit
	t = timeit.Timer('build(regexes)',setup='from __main__ import build, regexes')
	rep, num = 3, 10
	print("%.3f ms/build avg" % ( 1000*min(t.repeat(rep,num))/num ))

d = build(regexes)
for k,rm in d.items():
	r,m = rm
	print( "%-20s: %s" % ( k, r ))  # Regular Expression notation
	if verbose:
		print( str( m ))        # FSM transition table

def input_lines( prompt="--> "):
	line = input(prompt)
	while line:
		yield line
		line = input(prompt)

# If -i or -- "test" ... supplied, display how each composite FSM accepts each test
if interactive or tests:
	for line in tests if tests else input_lines():
		print("Testing w/: %r" % line )
		for k,rm in d.items():
			r,m = rm
			try:
				result = m.accepts(line)
			except Exception as e:
				result = repr( e )
			print("%-20s: %-20s: %s" % ( k, r, result))
