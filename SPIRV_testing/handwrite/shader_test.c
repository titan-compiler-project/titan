#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <spvm/context.h>
#include <spvm/state.h>
#include <spvm/ext/GLSL450.h>

// ripped straight from example file
spvm_source load_source(const char* fname, size_t* src_size) {
	FILE* f = fopen(fname, "rb");
	if (f == 0) {
		printf("Failed to load file %s\n", fname);
		return 0;
	}

	fseek(f, 0, SEEK_END);
	long file_size = ftell(f);
	fseek(f, 0, SEEK_SET);

	size_t el_count = (file_size / sizeof(spvm_word));
	spvm_source ret = (spvm_source)malloc(el_count * sizeof(spvm_word));
	fread(ret, el_count, sizeof(spvm_word), f);
	fclose(f);

	*src_size = el_count;

	return ret;
}

int main(int argc, char *argv[]){

    if (argc != 2) {
        printf("invalid set of arguments! expected 1, got %u\n", argc-1);
        return -1;
    }

    // context holds all opcode functions
	spvm_context_t ctx = spvm_context_initialize();

	// load source code
	size_t spv_length = 0;
	spvm_source spv = load_source(argv[1], &spv_length);

    // create a program and a state
	spvm_program_t prog = spvm_program_create(ctx, spv, spv_length);
	spvm_state_t state = spvm_state_create(prog);

    // load extension
	spvm_ext_opcode_func* glsl_ext_data = spvm_build_glsl450_ext();
	spvm_result_t glsl_std_450 = spvm_state_get_result(state, "GLSL.std.450");
	if (glsl_std_450)
		glsl_std_450->extension = glsl_ext_data;

    // call main
	spvm_word fnMain = spvm_state_get_result_location(state, "main");
	spvm_state_prepare(state, fnMain);
	spvm_state_call_function(state);

    // get c
	spvm_result_t c = spvm_state_get_result(state, "c");
	for (int i = 0; i < c->member_count; i++) {
		printf("FLOAT: %.2f\n", c->members[i].value.f);
		printf("INT: %i\n", c->members[i].value.s);
		// printf("uINT: %s", c->members[i].value.f);
	}
	printf("\n");
	// check if this pixel was discarded
	printf("discarded: %d\n", state->discarded);

    // free memory
	spvm_state_delete(state);
	spvm_program_delete(prog);
	free(glsl_ext_data);
	free(spv);

	spvm_context_deinitialize(ctx);

	return 0;
}
