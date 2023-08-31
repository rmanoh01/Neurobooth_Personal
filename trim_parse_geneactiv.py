import os
import re
import argparse
from functools import partial
from glob import glob
from tqdm.contrib.concurrent import process_map
from typing import NamedTuple


HEADER_N_LINES = 39
CLOCK_DRIFT_PATTERN = re.compile(r'device clock drift (\d+(\.\d+)?)s')


class ProcessFileResult(NamedTuple):
    """Bundled result of the process_file function"""
    input_path: str
    output_path: str
    excessive_drift: bool


class FileParseException(Exception):
    """Signals errors occurring during file processing"""
    pass


def main() -> None:
    args = parse_arguments()
    input_files = glob(os.path.join(args.input_dir, '*.bin'))
    _process_file = partial(process_file, output_dir=args.output_dir, clock_max_drift=args.clock_max_drift)
    results = process_map(_process_file, input_files, desc='Processing', unit='files', chunksize=1)

    # Make results spreadsheet
    with open(os.path.join(args.output_dir, 'results.csv'), 'w') as f:
        f.write('input_path, output_path, excessive_dift\n')
        for r in results:
            f.write(f'{r.input_path}, {r.output_path}, {r.excessive_drift}\n')


def process_file(input_path: str, output_dir: str, clock_max_drift: float) -> ProcessFileResult:
    """Checks to see if a trimmed version of the file already exists. If not, produces a trimmed file.
    :param input_path: The path to the file to trim/parse.
    :param output_dir: The output directory.
    :param clock_max_drift: The maximum (absolute) expected clock drift.
    :returns: True if the clock drift exceeds the maximum. False otherwise.
    """
    input_file = os.path.basename(input_path)
    output_path = os.path.join(output_dir, f'condensed_{input_file}')
    output_path_flagged = os.path.join(output_dir, f'flagged_condensed_{input_file}')

    # Skip processing the file if it has already been done
    if os.path.exists(output_path):
        return ProcessFileResult(input_path=input_path, output_path=output_path, excessive_drift=False)
    elif os.path.exists(output_path_flagged):
        return ProcessFileResult(input_path=input_path, output_path=output_path_flagged, excessive_drift=True)

    # Read in just the file header
    with open(input_path, 'r') as f_in:
        header = [f_in.readline() for _ in range(HEADER_N_LINES)]

    # Parse out the clock drift
    drift = None
    for line in header:
        match = re.search(CLOCK_DRIFT_PATTERN, line)
        if match is not None:
            drift = float(match.group(1))
            break

    if drift is None:
        raise FileParseException(f'Unable to locate a clock drift header line in {input_path}')

    # Write out the trimmed file
    excessive_drift = drift > clock_max_drift
    if excessive_drift:
        output_path = output_path_flagged
    with open(output_path, 'w') as f_out:
        f_out.writelines(header)

    return ProcessFileResult(input_path=input_path, output_path=output_path, excessive_drift=excessive_drift)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trim GENEActiv files and compile a list of problematic files.")
    parser.add_argument(
        '--input-dir',
        type=str,
        required=True,
        help='The directory containing raw .bin files.',
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='The directory to output trimmed .bin files and a spreadsheet of results.',
    )
    parser.add_argument(
        '--clock-max-drift',
        type=float,
        default=100,
        help='The maximum expected (absolute) clock drift of a recording.',
    )
    args = parser.parse_args()

    args.input_dir = os.path.abspath(args.input_dir)
    args.output_dir = os.path.abspath(args.output_dir)
    args.clock_max_drift = abs(args.clock_max_drift)

    if not os.path.exists(args.input_dir) or not os.path.isdir(args.input_dir):
        parser.error(f'{args.input_dir} is not a valid directory.')

    if not os.path.exists(args.output_dir):
        print(f'Creating output path: {args.output_dir}')
        os.makedirs(args.output_dir)

    return args


if __name__ == '__main__':
    main()
