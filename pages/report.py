import streamlit as st 
import gc

gc.collect()


def main():
    st.markdown(f'test')

if __name__ == '__main__':
    import warnings
    import gc
    warnings.filterwarnings("ignore") 

    gc.collect()

    main()