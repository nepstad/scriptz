from pylab import imread, imshow, connect, get_current_fig_manager, draw, \
		disconnect, gca
from numpy import log10, flipud, array, sqrt
import matplotlib

class DataPointsExtractor:
	"""
	Extracts data points from a bitmap figure. Initialize class object with a
	bitmap figure and axis extent. Then run Initialize() to start data point
	collection. First three clicks are used for calibration (xmin,ymin),
	(xmin,ymax), (xmax,ymin). Subsequent clicks are logged. Right click stops
	collection process. Finally run Analyze() to get the coordinate values.
	Note that zooming and panning is possible, as any clicks when in one of
	these modes is ignored.

	Usage example:
	    xmin = 0; ymin = 0; xmax = 2; ymax = 3
	    dpe = DataPointsExtractor("image.png", (xmin, ymin, xmax, ymax)
	    dpe.Initialize()
	    ...click...
	    X,Y dpe.Analyze()

	    The datapoints in the given coordinate system is then returned in X,
	    Y.
	"""

	def __init__(self, imfile, extent, logscaley=False, logscalex=False,
			drawindicators=True):
		self.DataPointsX = []
		self.DataPointsY = []
		self.Event = None
		self.EventId = 0
		self.ToolBar = 0
		self.ImageFile = imfile
		self.Extent = list(extent)
		self.LogScaleX = logscalex
		self.LogScaleY = logscaley
		self.DrawIndicators = drawindicators

		if self.LogScaleX:
			self.Extent[0] = log10(extent[0])
			self.Extent[2] = log10(extent[2])

		if self.LogScaleY:
			self.Extent[1] = log10(extent[1])
			self.Extent[3] = log10(extent[3])

	def Initialize(self):
		"""
		Load and display bitmap figure, and start data collection process.
		"""
		#Load and show data plot
		im = imread(self.ImageFile)
		imshow(flipud(im), origin="lower")
		self.EventId = connect("button_press_event", self.GetPosition)

		#Get toolbar handle
		self.ToolBar = get_current_fig_manager().toolbar

		print "First click on (x_min, y_min), then (x_min, y_max) and finally (x_max, y_min). This is used for calibration. Then click on all the datapoints. Right click when finished."

	def Analyze(self):
		"""
		Calculate collected coordinate values in specified coordinate system.
		"""

		#Get xmin and xmax of figure axis
		xPnts = array(self.DataPointsX[3:])
		xmin = self.DataPointsX[0]
		xmax = self.DataPointsX[2]

		#Get ymin and ymax of figure axis
		yPnts = array(self.DataPointsY[3:])
		ymin = self.DataPointsY[0]
		ymax = self.DataPointsY[1]

		#Transform datapoints to "actual" axis
		actualSpacingX = self.Extent[2] - self.Extent[0]
		actualSpacingY = self.Extent[3] - self.Extent[1]
		transformedX = actualSpacingX / (xmax-xmin) * (xPnts - xmin) + \
				self.Extent[0]
		transformedY = actualSpacingY / (ymax-ymin) * (yPnts - ymin) + \
				self.Extent[1]

		def ExpIfLog(data, var):
			if var:
				return 10**data
			else:
				return data

		return ExpIfLog(transformedX, self.LogScaleX), ExpIfLog(transformedY,
				self.LogScaleY)


	def GetPosition(self, event):
		"""
		Callback function for data point collection.
		"""
		try:
			line2d = matplotlib.lines.Line2D
			line2d = matplotlib.patches.Line2D
		except:
			pass

		#If we are zooming, do not register click
		if event.button == 1 and event.inaxes and self.ToolBar.mode == "":
			self.Event = event
			self.DataPointsX.append(event.xdata)
			self.DataPointsY.append(event.ydata)
			print "(x,y) = (%f, %f)" % (self.DataPointsX[-1],
					self.DataPointsY[-1])

			#Draw crossed circled at mouse click position
			if self.DrawIndicators:
				dx = 10
				dy = 10
				r = sqrt(dx**2 + dy**2)
				circ = matplotlib.patches.Circle((event.xdata, event.ydata),
						radius=r, fill=False, edgecolor="red", linewidth=2)
				lin1 = line2d(xdata=[event.xdata-dx,event.xdata+dx],
						ydata=[event.ydata-dy, event.ydata+dy], color="red",
						linewidth=1)
				lin2 = line2d(xdata=[event.xdata+dx,event.xdata-dx],
						ydata=[event.ydata-dy, event.ydata+dy], color="red",
						linewidth=1)
				ax = gca()
				ax.add_artist(circ)
				ax.add_artist(lin1)
				ax.add_artist(lin2)
				draw()

		#Right button click stops data point collection
		elif event.button == 3:
			disconnect(self.EventId)
			print "Finished collecting data points"
			print "Now run Analyse() to get point coordinates"

