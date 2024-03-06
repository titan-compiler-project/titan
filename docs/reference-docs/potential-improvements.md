# Potential improvements

This page serves as a way to keep track of what needs doing (i.e. what features to implement), and other potential improvements in the future to make the program more usable.

## On-going to-do list
- [ ] Arrays
    - [ ] declare size via decorator for arrays passed in as a parameter (needed because size & type must be known)
- [ ] Maps/loops without dependencies
- [ ] Automatic interface generation from template
- [ ] Total functional recursion
- [ ] Delayed inputs
- [ ] Rework verilog source code to use unpacked arrays in certain parts

## Improvements
- [ ] Rewrite in a typed language, potentially using the [C-API](https://docs.python.org/3/c-api/) to interface with the AST module.
- [ ] Better tests
- [ ] More varied sample code
- [ ] Add additional classes which inherit from the main Node class, and use them to correctly compile the relevant verilog code.