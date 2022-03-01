=====
Usage
=====

Objective and camera change can be accomplished by simply selecting the desired magnification and the camera in the user interface selector of the main **mctOptics** control screen:

.. image:: img/mctOptics.png 
   :width: 720px
   :align: center
   :alt: tomo_user

When changing lens/camera, **mctOptics** is also correcting for minor miss-alignment of the instrument visible light optics so that sample point of interest stays in the
center of the image at each lens change. **mctOptics** also keeps the rotation axis aligned with the detector columns and each lens/camera change by rotating the camera.

This capability allows for step-zoom-in during a tomographic measurement and shown in `this video <https://anl.box.com/s/7zr8oij9lavq7o7ylymy6qpbxqw1sz19>`_

The required lens offset sample x, y, z and the lens offset camera rotation are very reproducible and can be determined once when the instrument is first installed.



