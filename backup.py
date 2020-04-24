import datetime
import logging
import os
import threading

from pprint import pprint
from shutil import copyfile
from socket import gethostname
from time import sleep
from tqdm import tqdm
from tqdm.utils import _term_move_up

from backup_config import (
    source_dirs,
    backup_locs,
    exclude_file_types,
    log_setup,
    notes
)


def get_files(source_dirs):
    '''
    Recursively get the full path to every file in a list of directories.
    
    Parameters
    ----------
    source_dirs : tuple
        First element should be list of directories to search for files.
    
    Returns
    -------
    file_count : int
        The total number of files found.
    file_paths : list
        List of full paths to every file within a directory specified in
        directory_list.
    '''
    directory_list = []
    for entry in source_dirs:
        directory_list.append(entry[0])
    file_count = 0
    file_paths = []
    for directory in directory_list:
        for paths, _, files in os.walk(directory):
            file_count += len(files)
            for f in files:
                file_paths.append(os.path.join(paths, f))
    return file_count, file_paths


def make_backup_directory(backup_loc, timestamp):
    '''
    Make a timestamped backup directory within another directory.
    
    Parameters
    ----------
    backup_loc : str
        Path to directory within which to make a timestamped backup.
        
    Returns
    -------
    backup_dir : str
        Path to the timestamped backup directory.
    timestamp : str
        Formatted time stamp.
    '''
    backup_dir = os.path.join(
        backup_loc,
        timestamp
        # datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    )
    
    if not os.path.isdir(backup_dir):
        os.makedirs(backup_dir)
        
    return backup_dir


def make_backup_file_path(source_dirs, backup_dir, source_file_path):
    '''Generate a path to the backup location of a file.
    
    Each source directory supplied to the program is compared with the path to
    the file which is being backed up to see if it's a substring. If so, a new
    path is generated in the backup directory for this file to be copied to.
    
    Parameters
    ----------
    source_dirs : tuple
        First element should be list of source directories. Second element
        be the first subdirectory under the backup directory labelling this
        source.
    backup_dir : path
        Path to the backup directory.
    source_file_path : path
        Path to the file to be backed up.
    
    Raises
    ------
    ValueError
        If there is no matching source directory for file to be backed up.
    
    Returns
    -------
    backup_file_path : path
        Path to backup location of given source file.
    '''
    backup_file_path = None
    for source_dir in source_dirs:
        if source_file_path.find(source_dir[0]) is not -1:
            base_path = source_dir[1] + source_file_path[len(source_dir[0]):]
            backup_file_path = os.path.join(backup_dir, base_path)
            break
    if backup_file_path is None:
        raise ValueError('Something has gone horribly wrong.\nThis shouldn\'t'
                         +' be able to happen.')
    return backup_file_path


def check_excluded_filetype(f, exclude_file_types):
    '''Check to see if file type is in list of excluded types.
    
    Parameters
    ----------
    f : path
        Path to file.
    exclude_file_types : list
        List of strings of extensions of file types to exclude from the backup.
    
    Returns
    -------
    exclude_query : bool
        False if the file type is not in the list of excluded types. True
        otherwise.
    '''
    # get file extension
    ext = os.path.splitext(f)[-1].lower()
    
    # check if the file type is in the exclusion list
    if ext not in exclude_file_types:
        exclude_query = False  # don't skip
    else:
        exclude_query = True  # skip
    return exclude_query


def setup_log(log_location, log_level):
    '''Initialse a log.
    
    Parameters
    ----------
    log_location : path
        Path to log file.
    log_level : str
        Either ERROR, INFO or DEBUG.
    
    Raises
    ------
    ValueError
        If log_level is not ERROR, INFO or DEBUG.
    '''
    if log_level not in ['ERROR', 'INFO', 'DEBUG']:
        raise ValueError('Log level must be ERROR, INFO or DEBUG.')
    elif log_level == 'ERROR':
        level = logging.ERROR
    elif log_level == 'INFO':
        level = logging.INFO
    elif log_level == 'DEBUG':
        level = logging.DEBUG
    log_path = os.path.abspath(log_location)
    logging.basicConfig(filename=log_path,
                        level=level,
                        filemode='w')
    print('The logging level is set as {}\n'.format(log_level))


def backup_notes(backup_location,
                 source_dirs,
                 backup_locs,
                 excluded_types,
                 timestamp,
                 notes):
    '''Write notes on the backup to a file.
    
    Parameters
    ----------
    backup_location : str
        Where the current backup is being written.
    source_dirs : tuple
        First element is source directories. Second element is alias.
    backup_locs : list
        Elements are strings of backup locations.
    excluded_types : list
        List of strings of excluded file extensions.
    timestamp : str
        Timestamp string of this backup.
    notes : str
        Any notes to be written to this note file.
    '''
    note_file_name = 'backup_notes.txt'
    note_file_path = os.path.join(backup_location, note_file_name)
    with open(note_file_path, 'w') as f:
        f.write(  'Date\n'
                + '                 {}\n\n'.format(timestamp))
        f.write(  'Machine\n'
                + '                 {}\n\n'.format(gethostname()))
        f.write(  'Source folders\n')
        for i in range(len(source_dirs)):
            f.write('                 {}. {}\n'.format(i, source_dirs[i][0]))
        f.write('\n')
        f.write(  'Aliases\n')
        for i in range(len(source_dirs)):
            f.write('                 {}. {}\n'.format(i, source_dirs[i][1]))
        f.write('\n')
        f.write('Backup locations\n')
        for bup_loc in backup_locs:
            if bup_loc != backup_location:
                f.write('                 {}\n'.format(bup_loc))
            else:
                f.write('                 {} (here)\n'.format(bup_loc))
        f.write('\n')
        f.write(  'Excluded\n')
        for excl_type in excluded_types:
            f.write('                 {}\n'.format(excl_type))
        f.write('\n')
        f.write(  'Notes\n'
                + '                 {}'.format(notes))
        
    
def main():
    '''Create backups of source_dirs to backup_locs.'''
    # setting up log
    setup_log(log_setup[0], log_setup[1])
    
    print('Copying the following directores:')
    for entry in source_dirs:
        print('   \'{}\' as \'{}\''.format(entry[0], entry[1]))
        logging.info(' SOURCE: {}'.format(entry[0]))
        logging.info(' AS: {}'.format(entry[1]))
    print('')
    
    # make timestamped backup directories
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_dirs = []
    for dest in backup_locs:
        backup_dirs.append(make_backup_directory(dest, timestamp))    
    print('The following backup locations have been created:')
    for entry in backup_dirs:
        print('   \'{}\''.format(entry))
        logging.info(' BACKUP: {}'.format(entry))
    print('')

    # get paths to all the files to be backed up
    total_num_files, file_paths = get_files(source_dirs)
    print('Copying {} files to {} locations.'.format(total_num_files,
                                                     len(backup_locs)))
    logging.info(' FOUND {} FILES'.format(total_num_files))
    
    # keep track of failed copies
    failed_copies = 0
    
    # loop over each backup location
    for backup_dir in tqdm(backup_dirs,
                           desc='Backups',
                           leave=False):
        tqdm.write('\n')  # for tqdm
        backup_notes(backup_dir,
                     source_dirs,
                     backup_dirs,
                     exclude_file_types,
                     timestamp,
                     notes)
        
        # loop over each file
        for f in tqdm(file_paths,
                      desc='Files',
                      leave=False):
            # check if file type is in exclusion list
            logging.info(
                ' CHECKING IF {} IS OF AN EXCLUDED FILE TYPE'.format(f))
            
            if not check_excluded_filetype(f, exclude_file_types):
                logging.info(' INCLUDED')
                backup_file_path = make_backup_file_path(source_dirs,
                                                        backup_dir,
                                                        f)
                # make directory tree
                if not os.path.isdir(os.path.dirname(backup_file_path)):
                    logging.info(' MAKING DIRECTORY AT {}'.format(
                        os.path.dirname(backup_file_path)))
                    logging.debug(' MAKING DIRECTORY AT {}'.format(
                        os.path.dirname(backup_file_path)))
                    os.makedirs(os.path.dirname(backup_file_path))
                # copy the file
                logging.info(' ATTEMPTING TO COPY {} TO {}'.format(
                    f, backup_file_path))
                try:
                    copyfile(f, backup_file_path, follow_symlinks=False)
                    logging.info(' SUCCESS')
                except:
                    logging.error(' FAILED TO COPY {} TO {}'.format(
                        f, backup_file_path
                    ))
                    failed_copies += 1
            else:
                logging.info(' EXCLUDED')
                continue
            
            if log_setup[1] == 'DEBUG':
                sleep(1)
        
        tqdm_prefix = _term_move_up() + '\r'
        tqdm.write(tqdm_prefix + 'Completed backup to {}'.format(backup_dir))
    
    if failed_copies is 0:
        print('\nFinished with no failed copy actions')
    elif failed_copies is 1:
        print('\nFinished with 1 failed copy action')
    else:
        print('\nFinished with {} failed copy actions'.format(failed_copies))

    if failed_copies is not 0:
        print('See log file for details of failures')
    print('Exiting')
    

if __name__ == '__main__':
    main()
