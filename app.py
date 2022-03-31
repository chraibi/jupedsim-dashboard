import datetime as dt
import os
from collections import defaultdict
from io import StringIO
from pathlib import Path
from xml.dom.minidom import parseString
import timeit
import lovely_logger as logging
import numpy as np
import streamlit as st
from matplotlib import cm
from shapely.geometry import LineString
from copy import deepcopy
import plots
import Utilities
import doc

path = Path(__file__)
ROOT_DIR = path.parent.absolute()
home_path = str(Path.home())


@st.cache
def init_logger():
    T = dt.datetime.now()
    logging.info(f"init_logger at {T}")
    name = f"tmp_{T.year}-{T.month:02}-{T.day:02}_{T.hour:02}-{T.minute:02}-{T.second:02}.log"
    logfile = os.path.join(ROOT_DIR, name)
    logging.FILE_FORMAT = "[%(asctime)s] [%(levelname)-8s] - %(message)s"
    logging.DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    logging.init(logfile, to_console=False)

    return logfile


st.set_page_config(
    page_title="JuPedSim",
    page_icon=":large_blue_circle:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/jupedsim/jpscore",
        "Report a bug": "https://github.com/jupedsim/jpscore/issues",
        "About": "Open source framework for simulating, analyzing and visualizing pedestrian dynamics",
    },
)


def set_state_variables():
    if "old_data" not in st.session_state:
        st.session_state.old_data = ""

    if "data" not in st.session_state:
        st.session_state.data = []

    if "orig_data" not in st.session_state:
        st.session_state.orig_data = []

    if "geometry_data" not in st.session_state:
        st.session_state.geometry_data = ""

    if "geominX" not in st.session_state:
        st.session_state.geominX = -10

    if "geomaxX" not in st.session_state:
        st.session_state.geomaxX = 10

    if "geominY" not in st.session_state:
        st.session_state.geominY = -10

    if "geomaxY" not in st.session_state:
        st.session_state.geomaxY = 10

    if "geometry_wall" not in st.session_state:
        st.session_state.geometry_wall = 10

    if "transitions" not in st.session_state:
        st.session_state.transitions = []

    if "fps" not in st.session_state:
        st.session_state.fps = 16

    if "density" not in st.session_state:
        st.session_state.density = []

    if "tstats" not in st.session_state:
        st.session_state.tstats = defaultdict(list)

    if "cum_num" not in st.session_state:
        st.session_state.cum_num = {}

    if "unit" not in st.session_state:
        st.session_state.unit = "m"

    if "df" not in st.session_state:
        st.session_state.df = 12

    if "xpos" not in st.session_state:
        st.session_state.xpos = 0

    if "ypos" not in st.session_state:
        st.session_state.ypos = 0

    if "lm" not in st.session_state:
        st.session_state.lm = 0


def main():
    st.header(":information_source: Dashboard")
    info = st.expander("click to expand")
    with info:
        doc.docs()

    set_state_variables()
    st.sidebar.image("jupedsim.png", use_column_width=True)
    gh = "https://badgen.net/badge/icon/GitHub?icon=github&label"
    repo = "https://github.com/chraibi/jupedsim-dashboard"
    repo_name = f"[![Repo]({gh})]({repo})"
    st.sidebar.markdown(repo_name, unsafe_allow_html=True)
    c1, c2 = st.sidebar.columns((1, 1))
    trajectory_file = c1.file_uploader(
        "📙 Trajectory file ",
        type=["txt"],
        help="Load trajectory file",
    )
    # st.sidebar.markdown("-------")
    geometry_file = c2.file_uploader(
        "🏠 Geometry file ",
        type=["xml"],
        help="Load geometry file",
    )
    st.sidebar.markdown("-------")
    unit_pl = st.sidebar.empty()
    st.sidebar.header("📉 Plot")
    c1, c2 = st.sidebar.columns((1, 1))
    choose_trajectories = c1.checkbox(
        "Trajectories", help="Plot trajectories", key="Traj"
    )
    if choose_trajectories:
        choose_transitions = c2.checkbox(
            "Transitions", help="Show transittions", key="Tran"
        )

    pl_select_special_agent = st.sidebar.empty()
    pl_sample_trajectories = st.sidebar.empty()

    st.sidebar.markdown("-------")
    st.sidebar.header("🔵 Speed")
    how_speed_pl = st.sidebar.empty()
    df_pl = st.sidebar.empty()
    st.sidebar.markdown("-------")
    st.sidebar.header("🔴 Profiles")
    c1, c2 = st.sidebar.columns((1, 1))
    choose_dprofile = c1.checkbox(
        "Show", help="Plot density and speed profiles", key="dProfile"
    )
    # choose_vprofile = c2.checkbox("Speed", help="Plot speed profile", key="vProfile")
    choose_d_method = st.sidebar.radio(
        "Density method",
        ["Classical", "Gaussian", "Weidmann"],
        help="""
        How to calculate average of density over time and space""",
    )
    if choose_d_method == "Gaussian":
        width = st.sidebar.slider(
            "Width", 0.05, 1.0, 0.6, help="Width of Gaussian function"
        )

    dx = st.sidebar.slider("Grid size", 0.1, 1.0, 0.5, help="Space discretization")
    methods = ["nearest", "gaussian", "sinc", "bicubic", "mitchell", "bilinear"]
    interpolation = st.sidebar.radio(
        "Interpolation", methods, help="Interpolation method for imshow()"
    )
    if choose_dprofile:
        st.sidebar.markdown("-------")
        st.sidebar.header("📈 Timeseries (slow)")
        c1, c2 = st.sidebar.columns((1, 1))

        choose_timeseries = st.sidebar.checkbox(
            "🚦Plot", help="Plot density and speed timeseries", key="timeseries"
        )

    else:
        choose_timeseries = False

    c1, c2 = st.sidebar.columns((1, 1))
    posx_pl = c1.empty()
    posy_pl = c2.empty()
    side_pl = c1.empty()
    sample_pl = c2.empty()

    st.sidebar.markdown("-------")
    st.sidebar.header("📊 Plot curves")
    c1, c2 = st.sidebar.columns((1, 1))
    msg_status = st.empty()
    disable_NT_flow = False
    if trajectory_file and geometry_file:
        logging.info(f">> {trajectory_file.name}")
        logging.info(f">> {geometry_file.name}")
        try:

            h = st.expander("Head of Trajectories (first 4 columns)", expanded=True)
            stringio = StringIO(trajectory_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            if string_data != st.session_state.old_data:
                st.session_state.old_data = string_data
                new_data = True
                logging.info("Loading new trajectory data")
            else:
                new_data = False

            if Utilities.detect_jpscore(string_data):
                how_speed = how_speed_pl.radio(
                    "Source:", ["from simulation", "from trajectory"]
                )
                st.write(
                    "<style>div.row-widget.stRadio > div{flex-direction:row;}</style>",
                    unsafe_allow_html=True,
                )
                df = 10
            else:
                how_speed = how_speed_pl.radio(
                    "Source:", ["from trajectory", "from simulation"]
                )
                st.write(
                    "<style>div.row-widget.stRadio > div{flex-direction:row;}</style>",
                    unsafe_allow_html=True,
                )
                df = df_pl.slider(
                    "df",
                    2,
                    50,
                    10,
                    help="how many frames to consider for calculating the speed",
                )

            if new_data:
                with Utilities.profile("Load trajecgories"):
                    logging.info("Load trajectories ..")
                    data = Utilities.read_trajectory(trajectory_file)
                    st.session_state.orig_data = np.copy(data)
                    fps = Utilities.get_fps(string_data)
                    if data.shape[1] < 10:  # extend data
                        data = Utilities.compute_speed_and_angle(
                            data, fps, st.session_state.df
                        )

                    unit = Utilities.get_unit(string_data)
                    st.session_state.unit = unit
                    st.session_state.data = np.copy(data)
                    st.session_state.fps = fps
                    logging.info("Done loading trajectories")

            else:
                with Utilities.profile("Second init"):
                    data = np.copy(st.session_state.data)
                    fps = st.session_state.fps
                    unit = st.session_state.unit

            with h:
                with Utilities.profile("show_table"):
                    fig = plots.show_trajectories_table(data[:10, 0:5])
                    st.plotly_chart(fig, use_container_width=True)

            if unit not in ["cm", "m"]:
                unit = unit_pl.radio(
                    "What is the unit of the trajectories?",
                    ["cm", "m"],
                    help="Choose the unit of the original trajectories. Data in the app will be converted to meter",
                )
                st.write(
                    "<style>div.row-widget.stRadio > div{flex-direction:row;}</style>",
                    unsafe_allow_html=True,
                )
                st.sidebar.markdown("-------")

            st.markdown("### :bar_chart: Statistics")
            pl_msg = st.empty()
            frames = np.unique(data[:, 1])
            peds = np.unique(data[:, 0]).astype(int)
            nagents = len(peds)
            msg = f"""
            Unit: {unit}\n
            Frames per second: {fps}\n
            Frames: {len(frames)} | First: {frames[0]:.0f} | Last: {frames[-1]:.0f}\n
            Agents: {nagents}\n
            Evac-time: {np.max(frames)/fps} [s]
            """
            pl_msg.info(msg)
            if nagents <= 10:
                special_agent = 5
            else:
                special_agent = peds[10]

            sample_trajectories = pl_sample_trajectories.number_input(
                "sample",
                min_value=1,
                max_value=int(np.max(frames * 0.2)),
                value=10,
                step=5,
                help="Sample rate of ploting trajectories and time series \
                (the lower the slower)",
                key="sample_traj"
            )

            plot_ped = pl_select_special_agent.select_slider(
                "Highlight pedestrian", options=peds, value=(special_agent)
            )

            logging.info(f"fps = {fps}")
        except Exception as e:
            msg_status.error(
                f"""Can't parse trajectory file.
                Error: {e}"""
            )
            st.stop()

        try:
            parse_geometry_file = Utilities.get_geometry_file(string_data)
            logging.info(f"Geometry: <{geometry_file.name}>")
            # Read Geometry file
            if parse_geometry_file != geometry_file.name:
                st.error(
                    f"Mismatched geometry files. Parsed {parse_geometry_file}. Uploaded {geometry_file.name}"
                )
                st.stop()

            geo_stringio = StringIO(geometry_file.getvalue().decode("utf-8"))
            geo_string_data = geo_stringio.read()
            if geo_string_data != st.session_state.geometry_data:
                with Utilities.profile("Load geometry:"):
                    new_geometry = True
                    st.session_state.geometry_data = geo_string_data
                    # file_data = geometry_file.read()
                    geo_xml = parseString(geometry_file.getvalue())
                    logging.info("Geometry parsed successfully")
                    geometry_wall = Utilities.read_subroom_walls(geo_xml, unit="m")
                    logging.info("Got geometry walls successfully")
                    transitions = Utilities.get_transitions(geo_xml, unit="m")
                    logging.info("Got geometry transitions successfully")
                    measurement_lines = Utilities.get_measurement_lines(
                        geo_xml, unit="m"
                    )
                    logging.info("Got geometry measurement_lines successfully")
                    # todo: check if ids of transitions and measurement_lines are unique
                    transitions.update(measurement_lines)
                    logging.info("Get geo_limits")
                    geominX, geomaxX, geominY, geomaxY = Utilities.geo_limits(
                        geo_xml, unit="m"
                    )
                    st.session_state.geominX = geominX
                    st.session_state.geomaxX = geomaxX
                    st.session_state.geominY = geominY
                    st.session_state.geomaxY = geomaxY
                    st.session_state.transitions = deepcopy(transitions)
                    st.session_state.geometry_wall = deepcopy(geometry_wall)
                    logging.info(
                        f"GeometrySize: X: ({geominX:.2f},{geomaxX:.2f}), Y: ({geominY:.2f},{geomaxY:.2f})"
                    )
            else:
                with Utilities.profile("Second geome init"):
                    # new_geometry = False
                    geominX = st.session_state.geominX
                    geomaxX = st.session_state.geomaxX
                    geominY = st.session_state.geominY
                    geomaxY = st.session_state.geomaxY
                    geometry_wall = deepcopy(st.session_state.geometry_wall)
                    transitions = deepcopy(st.session_state.transitions)

            # select all per default
            if transitions:
                default = list(transitions.keys())  # choose this transition by default
            else:
                default = []
                disable_NT_flow = True

        except Exception as e:
            msg_status.error(
                f"""Can't parse geometry file.
                Error: {e}"""
            )
            st.stop()

        if unit == "cm":
            data[:, 2:4] /= 100
            data[:, -1] /= 100

            geominX /= 100
            geomaxX /= 100
            geominY /= 100
            geomaxY /= 100
            geometry_wall = {k: geometry_wall[k] / 100 for k in geometry_wall}
            transitions = {k: transitions[k] / 100 for k in transitions}
            logging.info(
                f"CM GeometrySize: X: ({geominX:.2f},{geomaxX:.2f}), Y: ({geominY:.2f},{geomaxY:.2f})"
            )

        NT_form = st.sidebar.form("plot-NT")
        with NT_form:
            choose_NT = c1.checkbox(
                "N-T", help="Plot N-t curve", key="NT", disabled=disable_NT_flow
            )
            choose_flow = c2.checkbox(
                "Flow", help="Plot flow curve", key="Flow", disabled=disable_NT_flow
            )
            choose_evactime = c1.checkbox(
                "Occupation",
                help="Plot number of pedestrians inside geometry over time",
                key="EvacT",
            )
            choose_survival = c2.checkbox(
                "Survival",
                help="Plot survival function (clogging)",
                key="Survival",
            )

        selected_transitions = NT_form.multiselect(
            "Select transition",
            transitions.keys(),
            default,
            help="Transition to calculate N-T. Can select multiple transitions",
        )
        make_plots = NT_form.form_submit_button(label="🚦plot")
        # ----- Jam
        st.sidebar.header("Jam")
        st.sidebar.slider(
            "Min jam speed",
            0.1,
            1.0,
            0.5,
            help="Agent slower that this speed is in jam",
            key="jVmin",
        )
        st.sidebar.slider(
            "Min jam duration",
            1,
            300,
            60,
            help="A jam last at least that long",
            key="jTmin",
        )
        st.sidebar.slider(
            "Min agents in jam",
            2,
            50,
            20,
            help="A jam has at least so many agents",
            key="jNmin",
        )

        if disable_NT_flow:
            st.sidebar.info(
                "N-T and Flow plots are disabled, \
            because no transitions!"
            )

        if how_speed == "from simulation":
            logging.info("speed by simulation")
            Utilities.check_shape_and_stop(data.shape[1], how_speed)
        else:
            logging.info("speed by trajectory")
            if df != st.session_state.df:
                data = Utilities.compute_speed_and_angle(
                    st.session_state.orig_data, fps, df
                )
                st.session_state.data = np.copy(data)
                st.session_state.df = df
                if unit == "cm":
                    data[:, 2:4] /= 100
                    data[:, -1] /= 100

        if choose_trajectories:
            agent = data[data[:, 0] == plot_ped]
            if how_speed == "from simulation":
                speed_agent = agent[:, 9]
                angle_agent = agent[:, 7]
            else:
                speed_agent = agent[:, -1]
                angle_agent = agent[:, -2]

            c1, c2 = st.columns((1, 1))
            with c1:
                with Utilities.profile("plot_trajectories"):
                    fig = plots.plot_trajectories(
                        data,
                        plot_ped,
                        speed_agent,
                        geometry_wall,
                        transitions,
                        geominX,
                        geomaxX,
                        geominY,
                        geomaxY,
                        choose_transitions,
                        sample_trajectories,
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                with Utilities.profile("plot_agent_xy"):
                    fig = plots.plot_agent_xy(
                        agent[::sample_trajectories, 1], agent[::sample_trajectories, 2], agent[:, 3], fps,
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with c1:
                with Utilities.profile("plot_agent_angle"):
                    fig = plots.plot_agent_angle(
                        plot_ped, agent[::sample_trajectories, 1], angle_agent[::sample_trajectories], fps,
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                with Utilities.profile("plot_agent_speed"):

                    fig = plots.plot_agent_speed(
                        plot_ped, agent[::sample_trajectories, 1], speed_agent[::sample_trajectories], np.max(data[:, -1]),
                        fps,
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # choose_dprofile =
        choose_vprofile = True  # todo: not sure is I want to keep this option
        if st.session_state.transitions:
            v = [x for x in transitions.values()]
            t = v[0]
            xm = np.sum(t[:, 0]) / 2
            ym = np.sum(t[:, 1]) / 2
        else:
            xm = 0.5 * (geominX + geomaxX)
            ym = 0.5 * (geominY + geomaxY)

        if choose_timeseries:
            xpos = posx_pl.number_input(
                "x-position of measurement area",
                min_value=float(geominX),
                max_value=float(geomaxX),
                value=xm,
                step=dx,
                format="%.1f",
                help="X-ccordinate of the center of the measurement square.",
            )
            ypos = posy_pl.number_input(
                "y-position of measurement area",
                min_value=float(geominY),
                max_value=float(geomaxY),
                value=ym,
                step=dx,
                format="%.1f",
                help="Y-ccordinate of the center of the measurement square.",
            )
            lm = side_pl.number_input(
                "side of square",
                min_value=0.5,
                max_value=5.0,
                value=1.0,
                step=0.5,
                format="%.1f",
                help="Length of the side of the measurement square.",
            )

            sample = sample_pl.number_input(
                "sample",
                min_value=1,
                max_value=int(np.max(frames * 0.2)),
                value=10,
                step=5,
                help="Sample rate of ploting time series \
                (the lower the slower)",
            )

            if xpos != st.session_state.xpos:
                st.session_state.xpos = xpos

            if ypos != st.session_state.ypos:
                st.session_state.ypos = ypos

            if lm != st.session_state.lm:
                st.session_state.lm = lm

        else:
            st.session_state.xpos = None
            st.session_state.ypos = None
            st.session_state.lm = None

        info = st.expander("Documentation: Profiles (click to expand)")
        with info:
            doc.doc_profile()

        if choose_dprofile:
            Utilities.check_shape_and_stop(data.shape[1], how_speed)
            msg = ""

            with st.spinner("Processing ..."):
                c1, _, c2 = st.columns((1, 0.05, 1))
                if choose_dprofile:
                    if choose_d_method == "Weidmann":
                        density_ret = \
                            Utilities.calculate_density_average_weidmann(
                                geominX,
                                geomaxX,
                                geominY,
                                geomaxY,
                                dx,
                                len(frames),
                                data[:, 2],
                                data[:, 3],
                                data[:, -1],
                            )
                        # time serie
                        if choose_timeseries:
                            density_time = []
                            for frame in frames[::sample]:
                                dframe = data[:, 1] == frame
                                x = data[dframe][:, 2]
                                y = data[dframe][:, 3]
                                speed_agent = data[dframe][:, -1]
                                dtime = Utilities.calculate_density_average_weidmann(
                                    st.session_state.xpos - st.session_state.lm / 2,
                                    st.session_state.xpos + st.session_state.lm / 2,
                                    st.session_state.ypos - st.session_state.lm / 2,
                                    st.session_state.ypos + st.session_state.lm / 2,
                                    st.session_state.lm,
                                    1,
                                    x,
                                    y,
                                    speed_agent,
                                )
                                density_time.append(dtime[0, 0])
                    elif choose_d_method == "Gaussian":
                        with Utilities.profile("density profile gauss"):
                            density_ret = Utilities.calculate_density_average_gauss(
                                geominX,
                                geomaxX,
                                geominY,
                                geomaxY,
                                dx,
                                len(frames),
                                width,
                                data[:, 2],
                                data[:, 3],
                            )
                        if choose_timeseries:
                            # time serie
                            with Utilities.profile("time series gauss"):
                                density_time = []
                                for frame in frames[::sample]:
                                    dframe = data[:, 1] == frame
                                    x = data[dframe][:, 2]
                                    y = data[dframe][:, 3]
                                    dtime = Utilities.calculate_density_average_gauss(
                                        st.session_state.xpos - st.session_state.lm / 2,
                                        st.session_state.xpos + st.session_state.lm / 2,
                                        st.session_state.ypos - st.session_state.lm / 2,
                                        st.session_state.ypos + st.session_state.lm / 2,
                                        st.session_state.lm,
                                        1,
                                        width,
                                        x,
                                        y,
                                    )
                                    density_time.append(dtime[0, 0])

                    elif choose_d_method == "Classical":
                        density_ret = Utilities.calculate_density_average_classic(
                            geominX,
                            geomaxX,
                            geominY,
                            geomaxY,
                            dx,
                            len(frames),
                            data[:, 2],
                            data[:, 3],
                        )
                        # time serie
                        density_time = []
                        if choose_timeseries:
                            for frame in frames[::sample]:
                                dframe = data[:, 1] == frame
                                x = data[dframe][:, 2]
                                y = data[dframe][:, 3]

                                dtime = Utilities.calculate_density_frame_classic(
                                    st.session_state.xpos - st.session_state.lm / 2,
                                    st.session_state.xpos + st.session_state.lm / 2,
                                    st.session_state.ypos - st.session_state.lm / 2,
                                    st.session_state.ypos + st.session_state.lm / 2,
                                    st.session_state.lm,
                                    x,
                                    y,
                                )
                                density_time.append(dtime[0, 0])
                    st.session_state.density = density_ret
                    msg += f"Density profile in range [{np.min(density_ret):.2f} : {np.max(density_ret):.2f}] [1/m^2]. \n"
                    with c1:
                        fig = plots.plot_profile_and_geometry(
                            geominX,
                            geomaxX,
                            geominY,
                            geomaxY,
                            geometry_wall,
                            st.session_state.xpos,
                            st.session_state.ypos,
                            st.session_state.lm,
                            density_ret,
                            interpolation,
                            cmap=cm.jet,
                            label=r"$\rho\; / 1/m^2$",
                            title="Density",
                            vmin=None,
                            vmax=None,
                        )
                        st.pyplot(fig)
                        if choose_timeseries:
                            fig = plots.plot_timeserie(
                                frames, density_time, fps, "Density / m / m",
                                np.min(density_ret),
                                np.max(density_ret)+2,
                            )
                            st.plotly_chart(fig, use_container_width=True)

                    if choose_vprofile:
                        if choose_d_method == "Gaussian":
                            speed_ret = Utilities.weidmann(st.session_state.density)
                            if choose_timeseries:
                                speed_time = Utilities.weidmann(np.array(density_time))
                        else:
                            speed_ret = Utilities.calculate_speed_average(
                                geominX,
                                geomaxX,
                                geominY,
                                geomaxY,
                                dx,
                                len(frames),
                                data[:, 2],
                                data[:, 3],
                                data[:, -1]
                            )
                            if choose_timeseries:
                                speed_time = []
                                for frame in frames[::sample]:
                                    dframe = data[:, 1] == frame
                                    x = data[dframe][:, 2]
                                    y = data[dframe][:, 3]
                                    speed_agent = data[dframe][:, -1]
                                    stime = Utilities.calculate_speed_average(
                                        st.session_state.xpos - st.session_state.lm / 2,
                                        st.session_state.xpos + st.session_state.lm / 2,
                                        st.session_state.ypos - st.session_state.lm / 2,
                                        st.session_state.ypos + st.session_state.lm / 2,
                                        st.session_state.lm,
                                        1,
                                        x,
                                        y,
                                        speed_agent,
                                    )
                                    speed_time.append(stime[0, 0])

                        with c2:
                            fig = plots.plot_profile_and_geometry(
                                geominX,
                                geomaxX,
                                geominY,
                                geomaxY,
                                geometry_wall,
                                st.session_state.xpos,
                                st.session_state.ypos,
                                st.session_state.lm,
                                speed_ret,
                                interpolation,
                                cmap=cm.jet, #.reversed(),
                                label=r"$v\; / m/s$",
                                title="Speed",
                                vmin=None,
                                vmax=None,
                            )
                            st.pyplot(fig)
                            if choose_timeseries:
                                fig = plots.plot_timeserie(
                                    frames, speed_time, fps, "Speed / m/s",
                                    np.min(speed_ret), np.max(speed_ret),
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        speed = data[:, -1]
                        msg += f"Speed profile in range [{np.min(speed_ret):.2f} : {np.max(speed_ret):.2f}] [m/s]. "
                        msg += f"Speed trajectory in range [{np.min(speed):.2f} : {np.max(speed):.2f}] [m/s]. "
                    st.info(msg)

        # todo
        info = st.expander("Documentation: Plot curves (click to expand)")
        with info:
            doc.doc_plots()
   
        choose_speed = True
        plot_options = choose_NT or choose_flow or choose_speed
        if make_plots and plot_options:
            # peds = np.unique(data)
            with Utilities.profile("calculate_NT_data"):
                tstats, cum_num, trans_used, max_len = Utilities.calculate_NT_data(
                    transitions, selected_transitions, data, fps
                )
            # st.session_state.tstats = tstats
            # st.session_state.cum_num = cum_num

        if make_plots:
            c1, c2 = st.columns((1, 1))
            with c1:
                if choose_NT and tstats:
                    fig = plots.plot_NT(tstats, cum_num, fps)
                    st.plotly_chart(fig, use_container_width=True)
            with c2:
                if choose_flow and tstats:
                    fig = plots.plot_flow(tstats, cum_num, fps)
                    st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns((1, 1))
        if make_plots and choose_evactime:
            peds_inside = []
            for frame in frames:
                d = data[data[:, 1] == frame][:, 0]
                peds_inside.append(len(d))

            with c1:
                fig = plots.plot_peds_inside(frames, peds_inside, fps)
                st.plotly_chart(fig, use_container_width=True)

        if make_plots and choose_survival:
            with c2:
                fig = plots.plot_survival(tstats, fps)
                st.plotly_chart(fig, use_container_width=True)

        # -- download stats
        if make_plots:
            if choose_NT:
                T = dt.datetime.now()
                n = trajectory_file.name.split(".txt")[0]
                file_download = f"{n}_{T.year}-{T.month:02}-{T.day:02}_{T.hour:02}-{T.minute:02}-{T.second:02}.txt"
                once = 0  # don't download if file is empty
                for i in selected_transitions:
                    if not trans_used[i]:
                        continue

                    if len(tstats[i]) < max_len:
                        tmp_stats = np.full(max_len, -1)
                        tmp_stats[: len(tstats[i])] = tstats[i]
                        tmp_cum_num = np.full(max_len, -1)
                        tmp_cum_num[: len(cum_num[i])] = cum_num[i]
                    else:
                        tmp_stats = tstats[i]
                        tmp_cum_num = cum_num[i]

                    if not once:
                        all_stats = np.vstack((tmp_stats, tmp_cum_num))
                        once = 1
                    else:
                        all_stats = np.vstack((all_stats, tmp_stats, tmp_cum_num))

                if selected_transitions and once:
                    passed_lines = [i for i in selected_transitions if trans_used[i]]
                    fmt = len(passed_lines) * ["%d", "%d"]
                    all_stats = all_stats.T
                    np.savetxt(
                        file_download,
                        all_stats,
                        fmt=fmt,
                        header=np.array2string(
                            np.array(passed_lines, dtype=int),
                            precision=2,
                            separator="\t",
                            suppress_small=True,
                        ),
                        comments="#",
                        delimiter="\t",
                    )
                    with open(file_download, encoding="utf-8") as f:
                        st.sidebar.download_button(
                            "Download statistics", f, file_name=file_download
                        )


        info = st.expander("Documentation: Jam (click to expand)")
        with info:
            doc.doc_jam()
       

if __name__ == "__main__":
    with Utilities.profile("Main"):
        main()
