"""
An example of highlighting "linked" artists. When one is selected, its partner
will be highlighted in addition to the original artist.  Illustrates
subclassing a DataCursor.
"""
import numpy as np
import matplotlib.pyplot as plt
import mpldatacursor

def main():
    fig, axes = plt.subplots(ncols=2)
    num = 5
    xy = np.random.random((num, 2))

    lines = []
    for i in range(num):
        line, = axes[0].plot((i + 1) * np.arange(10))
        lines.append(line)

    points = []
    for x, y in xy:
        point, = axes[1].plot([x], [y], linestyle='none', marker='o')
        points.append(point)

    MultiHighlight(zip(points, lines))
    plt.show()


class MultiHighlight(mpldatacursor.HighlightingDataCursor):
    """Highlight "paired" artists. When one artist is selected, both it and
    it's linked partner will be highlighted."""
    def __init__(self, paired_artists, **kwargs):
        """
        Initialization is identical to HighlightingDataCursor except for the
        following:

        Parameters:
        -----------
            paired_artists: a sequence of tuples of matplotlib artists
                Pairs of matplotlib artists to be highlighted.

        Additional keyword arguments are passed on to HighlightingDataCursor.
        The "display" keyword argument will be overridden to "single".
        """
        # Two-way lookup table
        self.artist_map = dict(paired_artists)
        self.artist_map.update([pair[::-1] for pair in self.artist_map.items()])

        kwargs['display'] = 'single'
        artists = self.artist_map.values()
        mpldatacursor.HighlightingDataCursor.__init__(self, artists, **kwargs)

    def show_highlight(self, artist):
        paired_artist = self.artist_map[artist]
        mpldatacursor.HighlightingDataCursor.show_highlight(self, artist)
        mpldatacursor.HighlightingDataCursor.show_highlight(self, paired_artist)

if __name__ == '__main__':
    main()
