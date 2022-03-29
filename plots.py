import lovely_logger as logging
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objs as go
import streamlit as st
from mpl_toolkits.axes_grid1 import make_axes_locatable
from plotly.subplots import make_subplots


def show_trajectories_table(data):
    headerColor = 'grey'
    fig = go.Figure(
        data=[go.Table
              (header=dict(
                  values=['<b>ID</b>', '<b>Frame</b>', '<b>X</b>', '<b>Y</b>'],
                  fill_color=headerColor,
                  font=dict(color='white', size=12),
              ),
               cells=dict(
                   values=[data[:, 0], data[:, 1], data[:, 2], data[:, 3]],
               )
               )
              ])
    st.plotly_chart(fig, use_container_width=True)

    
def plot_NT(Frames, Nums, fps):
    logging.info("plot NT-curve")
    fig = make_subplots(
        rows=1, cols=1, subplot_titles=["N-T"], x_title="Time / s", y_title="Number of pedestrians"
    )
    for i, frames in Frames.items():
        nums = Nums[i]
        if not frames:
            continue

        # extend the lines to 0
        if frames[0] > 0:
            frames = np.hstack(([0], frames))
            nums = np.hstack(([0], nums))

        trace = go.Scatter(
            x=np.array(frames) / fps,
            y=nums,
            mode="lines",
            showlegend=True,
            name=f"ID: {i}",
            line=dict(width=3),
        )
        fig.append_trace(trace, row=1, col=1)

    fig.update_layout(hovermode="x")
    st.plotly_chart(fig, use_container_width=True)



def plot_flow(Frames, Nums, fps):
    logging.info("plot flow-curve")
    fig = make_subplots(
        rows=1, cols=1, subplot_titles=["Flow"], x_title="Time / s", y_title="J / 1/s"
    )
    for i, frames in Frames.items():
        nums = Nums[i]
        if not frames:
            continue

        times = np.array(frames) / fps
        J = nums / times
        trace = go.Scatter(
            x=np.hstack(([0, times[0]], times)),
            y=np.hstack(([0, 0], J)),
            mode="lines",
            showlegend=True,
            name=f"ID: {i}",
            line=dict(width=3),
        )
        fig.append_trace(trace, row=1, col=1)

    fig.update_layout(hovermode="x")
    st.plotly_chart(fig, use_container_width=True)


def plot_peds_inside(frames, peds_inside, fps):
    logging.info("plot peds inside")
    fig = make_subplots(
        rows=1, cols=1, subplot_titles=["Discharge curve"], x_title="Time / s", y_title="Number of Pedestrians inside"
    )
    times = frames / fps
    trace = go.Scatter(
        x=times,
        y=peds_inside,
        mode="lines",
        showlegend=False,
        line=dict(width=3, color='royalblue'),
    )
    fig.append_trace(trace, row=1, col=1)
    fig.update_layout(hovermode="x")
    st.plotly_chart(fig, use_container_width=True)


def plot_timeserie(frames, t, fps, title):
    fig = make_subplots(
        rows=1, cols=1, x_title="Time / s", y_title=title
    )
    times = frames / fps
    trace = go.Scatter(
        x=times,
        y=t,
        mode="lines",
        showlegend=False,
        line=dict(width=3, color='royalblue'),
    )
    fig.append_trace(trace, row=1, col=1)
    fig.update_layout(hovermode="x")
    st.plotly_chart(fig, use_container_width=True)



def plot_agent_xy(frames, X, Y, fps):
    fig = make_subplots(specs=[[{"secondary_y": True}]],
        rows=1, cols=1, x_title="Time / s",
    )
    times = frames/fps
    traceX = go.Scatter(
        x=times,
        y=X,
        mode="lines",
        showlegend=True,
        name='X',
        line=dict(width=3, color='firebrick'),
    )
    traceY = go.Scatter(
        x=times,
        y=Y,
        mode="lines",
        name='Y',
        showlegend=True,
        line=dict(width=3, color='royalblue'),
    )
    fig.add_trace(traceX, row=1, col=1, secondary_y=False,)
    fig.add_trace(traceY, row=1, col=1, secondary_y=True,)
    # Set y-axes titles
    fig.update_yaxes(title_text="X", secondary_y=False)
    fig.update_yaxes(title_text="Y", secondary_y=True,)
    fig.update_layout(hovermode="x")
    st.plotly_chart(fig, use_container_width=True)


def plot_agent_angle(pid, frames, angles, fps):
    fig = make_subplots(
        rows=1, cols=1, x_title="Time / s", y_title=r"Angle / Degree",
    )
    times = frames/fps
    trace = go.Scatter(
        x=times,
        y=angles,
        mode="lines",
        showlegend=False,
        name=f"Agent: {pid:.0f}",
        line=dict(width=3, color='royalblue'),
    )
    fig.append_trace(trace, row=1, col=1)
    fig.update_layout(hovermode="x")
    st.plotly_chart(fig, use_container_width=True)


def plot_agent_speed(pid, frames, speed_agent, max_speed, fps):
    fig = make_subplots(
                    rows=1, cols=1, x_title="Time / s", y_title="Speed / m/s"
                )
    threshold = 0.5  # according to DIN19009-2
    logging.info(f"plot agent speed {pid}")
    m = np.copy(speed_agent)
    times = frames / fps
    tt = np.ones(len(speed_agent))*threshold
    cc = np.isclose(m, tt, rtol=0.04)
    m[~cc] = None
    trace = go.Scatter(
        x=times,
        y=speed_agent,
        mode="lines",
        showlegend=False,
        name=f"Agent: {pid:.0f}",
        line=dict(width=3, color='royalblue'),
        stackgroup='one'
    )
    trace_threshold = go.Scatter(
        x=[times[0], times[-1]],
        y=[threshold, threshold],
        mode="lines",
        showlegend=True,
        name="Jam threshold",
        line=dict(width=4, dash='dash', color="gray"),
    )
    tracem = go.Scatter(
        x=times,
        y=m,
        mode="markers",
        showlegend=False,
        name="Jam speed",
        marker=dict(size=5,  color="red"),
    )
    fig.append_trace(trace, row=1, col=1)
    fig.append_trace(trace_threshold, row=1, col=1)
    fig.append_trace(tracem, row=1, col=1)
    fig.update_yaxes(
        range=[0, max_speed + 0.01],
    )
    fig.update_layout(hovermode="x")
    st.plotly_chart(fig, use_container_width=True)


# marker=dict(size=5, color=np.where(speed_agent >= threshold, 'blue', 'red')),


def plot_trajectories(data, special_ped, speed, geo_walls, transitions, min_x, max_x, min_y, max_y):
    fig = make_subplots(rows=1, cols=1)
    peds = np.unique(data[:, 0])
    s = data[data[:, 0] == special_ped]
    sc = 1-speed/np.max(speed)
    for ped in peds:
        d = data[data[:, 0] == ped]
        #c = d[:, -1]
        trace = go.Scatter(
            x=d[:, 2],
            y=d[:, 3],
            mode="lines",
            showlegend=False,
            name=f"Agent: {ped:0.0f}",
            line=dict(color="gray", width=0.3),
        )
        fig.append_trace(trace, row=1, col=1)

    trace = go.Scatter(
        x=s[:, 2],
        y=s[:, 3],
        mode="markers",
        showlegend=False,
        name=f"Agent: {special_ped:0.0f}",
        marker=dict(size=5, color=sc, colorscale='Jet'),
        line=dict(color="firebrick", width=4),
    )
    fig.append_trace(trace, row=1, col=1)

    for gw in geo_walls.keys():
        trace = go.Scatter(
            x=geo_walls[gw][:, 0],
            y=geo_walls[gw][:, 1],
            showlegend=False,
            mode="lines",
            line=dict(color="black", width=2),
        )
        fig.append_trace(trace, row=1, col=1)

    for i, t in transitions.items():
        xm = np.sum(t[:, 0]) / 2
        ym = np.sum(t[:, 1]) / 2
        length = np.sqrt(np.diff(t[:, 0]) ** 2 + np.diff(t[:, 1]) ** 2)
        offset = 0.1 * length[0]
        logging.info(f"offset transition {offset}")
        trace = go.Scatter(
            x=t[:, 0],
            y=t[:, 1],
            showlegend=False,
            name=f"Transition: {i}",
            mode="lines+markers",
            line=dict(color="red", width=3),
            marker=dict(color="black", size=5),
        )
        trace_text = go.Scatter(
            x=[xm + offset],
            y=[ym + offset],
            text=f"{i}",
            textposition="middle center",
            showlegend=False,
            mode="markers+text",
            marker=dict(color="red", size=0.1),
            textfont=dict(color="red", size=18),
        )
        fig.append_trace(trace, row=1, col=1)
        fig.append_trace(trace_text, row=1, col=1)

    eps = 1
    fig.update_yaxes(
        range=[min_y - eps, max_y + eps],
    )
    fig.update_xaxes(
        range=[min_x - eps, max_x + eps],
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_geometry(ax, _geometry_wall):
    for gw in _geometry_wall.keys():
        ax.plot(_geometry_wall[gw][:, 0], _geometry_wall[gw][:, 1], color="white", lw=2)


def plot_profile_and_geometry(
    geominX,
    geomaxX,
    geominY,
    geomaxY,
    geometry_wall,
    xpos,
    ypos,
    lm,
    data,
    interpolation,
    cmap,
    label,
    title,
    vmin=None,
    vmax=None,
):
    """Plot profile + geometry for 3D data


    if vmin or vmax is None, extract values from <data>
    """

    if vmin is None or vmax is None:
        vmin = np.min(data)
        vmax = np.max(data)

    fig, ax = plt.subplots(1, 1)
    im = ax.imshow(
        data,
        cmap=cmap,
        interpolation=interpolation,
        origin="lower",
        vmin=vmin,
        vmax=vmax,
        extent=[geominX, geomaxX, geominY, geomaxY],
    )
    plot_geometry(ax, geometry_wall)
    plot_square(ax, xpos, ypos, lm)
    ax.set_title(title)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3.5%", pad=0.3)
    cb = plt.colorbar(im, cax=cax)
    cb.set_label(label, rotation=90, labelpad=15, fontsize=15)
    st.pyplot(fig)


def plot_square(ax, xpos, ypos, lm):
    x = [xpos - lm/2,
         xpos - lm/2,
         xpos + lm/2,
         xpos + lm/2,
         xpos - lm/2,]
    y = [ypos - lm/2,
         ypos + lm/2,
         ypos + lm/2,
         ypos - lm/2,
         ypos - lm/2,]
    ax.plot(x, y, color="gray", lw=2)