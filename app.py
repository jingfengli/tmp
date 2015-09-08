
import flask

from bokeh.embed import components
from bokeh.plotting import *
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
from bokeh.util.string import encode_utf8
import pandas as pd
import simplejson
import requests


app = flask.Flask(__name__)

@app.route("/")
def stock():
    """ Very simple plot of stock closing price for last month or so"""
    # Grab the inputs arguments from the URL
    # This is automated by the button
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    if 'company' in args.keys() and args['company']:
        company = args['company']
    else:
        company = 'GOOG'

    cl = requests.get("https://www.quandl.com/api/v3/datasets/WIKI/%s.json?order=asc&rows=31&start_date=2015-07-01&end_date=2015-09-03" % (company))
    if cl.status_code == 200:
    	c2=cl.content
    	stock=simplejson.loads(c2)
    	abb=stock['dataset']['dataset_code']
    	datanames=stock['dataset']['column_names']
    	data=stock['dataset']['data']
    	dataorg=pd.DataFrame(data,columns=datanames)
    	dataorg['Date']=pd.to_datetime(dataorg['Date'])
    else:
        ######## THIS IS NOT RECOMMENDED, because now it just returns an error message if not find the ticker.
        return 'Error! Ticker does not exist!'


    # Create a graph
    fig = figure(x_axis_type="datetime")
    fig.line(dataorg.Date,dataorg.Close)
    fig.title="Stock closing price (%s), from 07-01-2015    " % (company)
    # fig.xaxis_axis_label='Date'
    # fig.yaxis_axis_label='Price'

    # Configure resources to include BokehJS inline in the document.
    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/reference/resources_embedding.html#module-bokeh.resources
    plot_resources = RESOURCES.render(
        js_raw=INLINE.js_raw,
        css_raw=INLINE.css_raw,
        js_files=INLINE.js_files,
        css_files=INLINE.css_files,
    )

    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/user_guide/embedding.html#components
    script, div = components(fig, INLINE)
    html = flask.render_template(
        'embed.html',
        plot_script=script, plot_div=div, plot_resources=plot_resources,
        # color=color,
        company=company
    )
    return encode_utf8(html)


def main():
    app.debug = True
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
