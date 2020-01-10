/* -*- Mode: C; c-basic-offset:4 ; indent-tabs-mode:nil ; -*- */
/* 
 *
 *   Copyright (C) 1997 University of Chicago. 
 *   See COPYRIGHT notice in top-level directory.
 */

#include "mpioimpl.h"

#ifdef HAVE_WEAK_SYMBOLS

#if defined(HAVE_PRAGMA_WEAK)
#pragma weak MPI_File_write_all_begin = PMPI_File_write_all_begin
#elif defined(HAVE_PRAGMA_HP_SEC_DEF)
#pragma _HP_SECONDARY_DEF PMPI_File_write_all_begin MPI_File_write_all_begin
#elif defined(HAVE_PRAGMA_CRI_DUP)
#pragma _CRI duplicate MPI_File_write_all_begin as PMPI_File_write_all_begin
/* end of weak pragmas */
#endif

/* Include mapping from MPI->PMPI */
#define MPIO_BUILD_PROFILING
#include "mpioprof.h"
#endif

/*@
    MPI_File_write_all_begin - Begin a split collective write using
    individual file pointer

Input Parameters:
. fh - file handle (handle)
. buf - initial address of buffer (choice)
. count - number of elements in buffer (nonnegative integer)
. datatype - datatype of each buffer element (handle)

.N fortran
@*/
int MPI_File_write_all_begin(MPI_File fh, const void *buf, int count,
			     MPI_Datatype datatype)
{
    int error_code;
    static char myname[] = "MPI_FILE_WRITE_ALL_BEGIN";

    error_code = MPIOI_File_write_all_begin(fh, (MPI_Offset) 0,
					    ADIO_INDIVIDUAL, buf, count,
					    datatype, myname);

    return error_code;
}

/* prevent multiple definitions of this routine */
#ifdef MPIO_BUILD_PROFILING
int MPIOI_File_write_all_begin(MPI_File fh,
			       MPI_Offset offset,
			       int file_ptr_type,
			       const void *buf,
			       int count,
			       MPI_Datatype datatype,
			       char *myname)
{
    int error_code, datatype_size;
    ADIO_File adio_fh;
    void *e32buf=NULL;
    const void *xbuf=NULL;

    MPIU_THREAD_CS_ENTER(ALLFUNC,);

    adio_fh = MPIO_File_resolve(fh);

    /* --BEGIN ERROR HANDLING-- */
    MPIO_CHECK_FILE_HANDLE(adio_fh, myname, error_code);
    MPIO_CHECK_COUNT(adio_fh, count, myname, error_code);
    MPIO_CHECK_DATATYPE(adio_fh, datatype, myname, error_code);
    MPIO_CHECK_NOT_SEQUENTIAL_MODE(adio_fh, myname, error_code);

    if (file_ptr_type == ADIO_EXPLICIT_OFFSET && offset < 0)
    {
	error_code = MPIO_Err_create_code(MPI_SUCCESS, MPIR_ERR_RECOVERABLE,
					  myname, __LINE__, MPI_ERR_ARG,
					  "**iobadoffset", 0);
	error_code = MPIO_Err_return_file(adio_fh, error_code);
	goto fn_exit;
    }

    if (adio_fh->split_coll_count)
    {
	error_code = MPIO_Err_create_code(MPI_SUCCESS, MPIR_ERR_RECOVERABLE,
					  myname, __LINE__, MPI_ERR_IO, 
					  "**iosplitcoll", 0);
	error_code = MPIO_Err_return_file(adio_fh, error_code);
	goto fn_exit;
    }
    /* --END ERROR HANDLING-- */

    adio_fh->split_coll_count = 1;

    MPI_Type_size(datatype, &datatype_size);
    /* --BEGIN ERROR HANDLING-- */
    MPIO_CHECK_INTEGRAL_ETYPE(adio_fh, count, datatype_size, myname, error_code);
    MPIO_CHECK_COUNT_SIZE(adio_fh, count, datatype_size, myname, error_code);
    /* --END ERROR HANDLING-- */


    xbuf = buf;
    if (adio_fh->is_external32) {
	error_code = MPIU_external32_buffer_setup(buf, count, datatype, &e32buf);
	if (error_code != MPI_SUCCESS) 
	    goto fn_exit;

	xbuf = e32buf;
    }

    adio_fh->split_datatype = datatype;
    ADIO_WriteStridedColl(adio_fh, xbuf, count, datatype, file_ptr_type,
			  offset, &adio_fh->split_status, &error_code);

    /* --BEGIN ERROR HANDLING-- */
    if (error_code != MPI_SUCCESS)
	error_code = MPIO_Err_return_file(adio_fh, error_code);
    /* --END ERROR HANDLING-- */

fn_exit:
    if ( e32buf != NULL) ADIOI_Free(e32buf);
    MPIU_THREAD_CS_EXIT(ALLFUNC,);

    return error_code;
}
#endif
