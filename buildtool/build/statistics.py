from collections import defaultdict

import numpy as np

from buildtool.build.common import BuildContext


def print_build_statistics(context: BuildContext) -> None:
    print_image_statistics(context)


def print_image_statistics(context: BuildContext) -> None:
    image_file_sizes_by_tag: defaultdict[str, list[int]] = defaultdict(list)
    for srcset in context.state.image_srcsets.values():
        for entry in srcset:
            image_file_sizes_by_tag[entry.descriptor].append(context.build_dir.resolve_url_path(entry.url).stat().st_size)
    averages = {tag: np.mean(sizes) for tag, sizes in image_file_sizes_by_tag.items()}

    print(f'Image srcset average files sizes:')
    for tag in sorted(averages.keys(), key=lambda t: (len(t), t)):
        avg = averages[tag]
        print(f'{tag}: {int(avg / 1000)}KB')
