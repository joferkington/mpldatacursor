Current Development Version
---------------------------

8/16/2015
        Added basic support for getting the z-value of 3D artists.

8/16/2015
        Made annotation boxes try to stay visible by flipping the xytext value.
        The *keep_inside* kwarg controls whether or not this happens.  Note
        that this is a slight change to the default functionality: If the x,y
        offset is adjusted to keep the text box visible, that offset will
        "stick".  If you'd prefer the text box to _always_ be to the
        upper-left/etc of the clicked point, set ``keep_inside=False``.
        Thanks to AgilentGCMS for the suggestion!

7/26/2014
        Made default formatter function handle unicode properly. Thanks to
        Benjamin Chrétien for the catch!  Due to the way I've currently
        implemented this (explicitly unicode literals), it makes mpldatacursor
        incompatible with python 3.0, 3.1, and 3.2.  However, compatibility
        with python 2.6, 2.7, 3.3, and 3.4 will be maintained.  I may change
        this in the future, but for the moment, be aware that the development
        version current supports >3.3, but not 3.0, 3.1, or 3.2.

6/16/2014
        Added workaround to ensure that mpldatacursor works properly with
        twinned axes.  Thanks to Nils Wagner for the bug report!

4/26/2014
        Specific annotation boxes can now be hidden by right-clicking. Added
        "hide_button" and "display_button" options to control exactly which
        mouse buttons show/hide annotation boxes. Now _only_ a specific mouse
        button ("display_button", which defaults to 1) will display a
        datacursor, rather than any mouse button triggering a display. Thanks
        to Joe Louderback for the idea and initial pull request.

3/12/2014
        Made datacursor auto-detect if the x or y axes are set to display dates
        and format the coordinate as a date if so. Also added the "date_format"
        kwarg to control the date formatting. Kudos to Doug Hoffman for the
        suggestion.

2/11/2014
        Fixed bug with bar plots not displaying legend labels. Kudos to 
        Nils Wagner for the catch.

Version 0.5
-----------

1/5/2014
        Enabled keyboard shortcuts by default. "d" hides/deletes visible
        annotation boxes, while "t" toggles interactivity.

1/5/2014
        Added the ``props_override`` option to customize the x,y location where
        the popup is displayed without subclassing or monkey-patching
        mpldatacursor.

1/5/2014
        Fixed bug with bar plots and made width, height, etc be passed in to
        the formatter function for Rectangle artists.

1/2/2014
        Added basic support for allowing datacursors to pop up on hover.

12/29/2013
        Made the ``bbox`` and ``arrowprops`` arguments use the mpldatacursor
        defaults as a "base".  Therefore, specifying something like
        ``bbox=dict(alpha=1)`` will result in a yellow, opaque box with rounded
        corners instead of a blue, square box.

12/22/2013
        Added a workaround for a bug in the OSX backend that causes a segfault.

12/17/2013
        Alessandro Impellizzeri switched things to use relative imports for
        compatibility with python 3.x.

11/15/2013
        Made x,y position of annotate snap to the displayed x,y values
        Thanks to megies for the bug report and suggestion!

10/7/2013
        Fixed bug in line interpolation. Kudos to dand-oss for the catch.

8/20/2013
        Bugfix for images with matplotlib 1.3.

7/30/2013
        Refactored mpldatacursor into multiple files.

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
