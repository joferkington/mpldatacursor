Version 0.4.2
-------------
12/23/2013
        Backported a bugfix to workaround a segfault in the OSX backend.

Version 0.4.1
-------------

8/20/13
        Backported a bugfix to allow compability with matplotlib-1.3.x.

Version 0.4
-----------

7/18/2013
        Ehsan Azar added rate-limit to avoid multiple calls and resulting
        "animation effect" when multiple artists are selected. 

7/15/2013
        Added support for displaying non-scalar z-values (e.g. R,G,B).  Kudos
        to Ivan Panchenko for the suggestion.

7/13/2013
        Fixed major bug in image handling. Incorrect z-values were being
        displayed for non-square images. 

6/22/2013
        Added hiding and disabling functionality.  New methods:
        datacursor.hide(), datacursor.enable(), and datacursor.disable() as
        well as datacursor.enabled property Kudos to Joe Louderback for the
        suggestion.

6/22/2013
        Added ``point_labels`` kwarg and functionality.  New ``point_labels``
        kwarg that allows labels for the "subitems" of an artist (e.g. points
        in a ``Line2D``) to be individually labeled.
   
Version 0.3
-----------

5/19/2013
        ``pcolor`` and ``pcolormesh`` support.  Added support for "z" info for
        ``pcolor`` and ``pcolormesh`` plots.

5/18/2013
        ``contour`` and ``contourf`` support.  Added support for "z" info for
        ``contour`` and ``contourf`` plots.  Unfortunately, these artists can
        only be picked when an "edge" is clicked on, so ``contourf`` support is
        less than ideal.

3/9/2012
        Removed redundant ``template`` and ``offsets`` kwargs in favor of the
        ``foramtter`` kwarg.

Version 0.2
-----------

3/4/13
        Added ``datacursor`` convenience function, which automatically connects
        a datacursor to all plotted matplotlib artists.

2/28/13
        Made draggable datacursors a kwarg option instead of a separate class.

Version 0.1
-----------

2/21/2013
        Initial commit in git

1/22/2012
        Many minor updates.
        See http://stackoverflow.com/revisions/4674445/3

1/12/2011
        Initial version.
        See http://stackoverflow.com/revisions/4674445/1
