from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

from common.options import Options

class CompilerContext():

    compiler_args, name_of_top_module = None, None
    options, output_options, files, parsed_modules, functions = [], [], [], [], []


    def __init__(self, args: Namespace = None):
        """ Init function for the CompilerContext class.
        
            Args:
                args: Arguments to keep track of.

            Attributes:
                compiler_args: Arguments passed to the class.
                name_of_top_module: The name of the top module/function in the hierarchy.
                options: Parsed list of options provided by the user.
                output_options: Parsed list of output options provided by the user.
                files: List of files to process.
                parsed_modules: TODO
                functions: TODO
        """

        self.compiler_args = args
        self._legacy_arg_setter()

    def _legacy_arg_setter(self):
        """ Method to set the arguments due to legacy issues.
        
            Automatically populates the relevant attributes, using the arguments that
            were given during object instantiation.

            (I changed my mind about the original implementation,
            so this is a small workaround.)
        """
        if self.compiler_args.top is not None:
            self.options.append(Options.DEFINE_TOP_MODULE)
            self.name_of_top_module = self.compiler_args.top

        if self.compiler_args.asm:
            self.output_options.append(Options.OUTPUT_SPIRV_ASM)

        self.files.append(self.compiler_args.source_file)

    def user_wants_spirv_asm(self) -> bool:
        """ Getter function to see if user wants compiler to output SPIR-V assembly.

            Returns:
                True if user wants assembly, otherwise false.
        """
        return self.compiler_args.asm
    
    def has_user_defined_top(self) -> bool:
        """ Getter function to see if user defined a name for the top module.

            Returns:
                True if user defined a name, otherwise false.
        """
        return self.compiler_args.top is not None
    
    def get_top_module_name(self) -> str:
        """ Getter function to fetch top module name.
        
            Returns:
                Name of the top module as defined by the user.
        """
        return self.compiler_args.top
    
    def user_only_wants_spirv(self) -> bool:
        """ Getter function to see if user only wants to run the SPIR-V portion of the compiler. 
        
            Returns:
                True if user wants only SPIR-V, otherwise False.
        """
        return self.compiler_args.s
    
    def user_wants_verbose_info(self) -> bool:
        """ Getter function to see if user wants verbose debugging information.
        
            Returns:
                True if user wants debug info, else False.
        """
        return self.compiler_args.verbose