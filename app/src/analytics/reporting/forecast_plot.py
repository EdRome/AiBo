import streamlit as st
import plotly.graph_objects as go
import locale
import pandas as pd
locale.setlocale( locale.LC_ALL, '' )

def generate_last_month_forecast_dataframe(df: dict, forecast_df):
    df = pd.DataFrame(df)

    date_col = st.session_state["date_column"]
    last_date = df[date_col].max()

    last_month = last_date - pd.DateOffset(months=1)
    df_last_month = df[df[date_col] >= last_month]
    df_last_month_sales = df_last_month.groupby(st.session_state["product_column"]).agg(
        quantity = (st.session_state["quantity_column"], "sum"),
        amount = (st.session_state["amount_column"], "mean"),
    )

    df_last_month_sales = df_last_month_sales.merge(forecast_df, on=st.session_state["product_column"], how="left")
    return df_last_month_sales

def forecast_plot(forecast_df, product_col, start_idx, end_idx, item_name, TOTAL_ITEMS):

    # Crear gráfico
    fig = go.Figure()

    if item_name is not None or item_name != "":
        data = forecast_df[forecast_df[product_col] == item_name][product_col]
        values = forecast_df[forecast_df[product_col] == item_name]["forecast_quantity"]

        fig.add_trace(go.Bar(
            x=data,
            y=values,
            name=f"Forecast {item_name}"
        ))

    if item_name is None or item_name == "":
        fig.add_trace(go.Bar(
            x = forecast_df.iloc[start_idx:end_idx][product_col],
            y = forecast_df.iloc[start_idx:end_idx]["forecast_quantity"],
            name="Forecast"
        ))

    fig.update_layout(
        title=f"Products {start_idx+1}-{min(end_idx, TOTAL_ITEMS)} of {TOTAL_ITEMS}",
        xaxis_title="Products",
        yaxis_title="Forecast Quantity",
        height=600
    )

    return fig

def products_without_sales_last_month_plot(df):
    last_date = df[st.session_state["date_column"]].max()
    last_month = last_date - pd.DateOffset(months=1)
    df_last_month = df[df[st.session_state["date_column"]] >= last_month]
    total_products = st.session_state["unique_items"]
    products_with_sales = df_last_month[st.session_state["product_column"]].unique()

    productos_sin_ventas = [product for product in total_products if product not in products_with_sales]

    # Crear DataFrame con información adicional
    resultado = []
    for producto in productos_sin_ventas:
        # Obtener histórico del producto
        historico_producto = df[df[st.session_state["product_column"]] == producto]
        
        # Última fecha de venta
        ultima_venta = historico_producto[st.session_state["date_column"]].max()
        
        # Días desde última venta
        dias_sin_vender = (last_date - ultima_venta).days
        
        # Ventas totales históricas
        ventas_totales = historico_producto[st.session_state["quantity_column"]].sum()
        
        # Promedio mensual de ventas
        ventas_mensual_promedio = historico_producto.groupby(
            historico_producto[st.session_state["date_column"]].dt.to_period('M')
        )[st.session_state["quantity_column"]].sum().mean()
        
        resultado.append({
            'producto': producto,
            'ultima_venta': ultima_venta,
            'dias_sin_vender': dias_sin_vender,
            'ventas_totales_historicas': ventas_totales,
            'ventas_mensual_promedio': ventas_mensual_promedio,
            'meses_sin_ventas': dias_sin_vender // 30
        })
    
    return pd.DataFrame(resultado)

def products_with_increasing_demand_plot(df=None, forecast_df=None, df_last_month_sales=None):
    if df_last_month_sales is None:
        last_month = df[st.session_state["date_column"]].max() - pd.DateOffset(months=1)
        df_last_month = df[df[st.session_state["date_column"]] >= last_month]
        df_last_month_sales = df_last_month.groupby(st.session_state["product_column"]).agg(
            quantity = (st.session_state["quantity_column"], "sum"),
            amount = (st.session_state["amount_column"], "mean"),
        )

        df_last_month_sales = df_last_month_sales.merge(forecast_df, on=st.session_state["product_column"], how="left")

    df_last_month_sales["difference"] = df_last_month_sales["forecast_quantity"] - df_last_month_sales["quantity"]
    df_last_month_sales["difference_percentage"] = df_last_month_sales["difference"]/df_last_month_sales["quantity"]
    
    df_last_month_sales = df_last_month_sales.sort_values(by="quantity", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_last_month_sales[st.session_state["product_column"]],
        y=df_last_month_sales[st.session_state["quantity_column"]],
        name="Last month demand",
    ))

    fig.add_trace(go.Bar(
        x=df_last_month_sales[st.session_state["product_column"]],
        y=df_last_month_sales["forecast_quantity"],
        name="Forecast demand",
    ))

    return fig

def products_with_decreasing_demand_plot(df=None, forecast_df=None, df_last_month_sales=None):
    if df_last_month_sales is None:
        last_month = df[st.session_state["date_column"]].max() - pd.DateOffset(months=1)
        df_last_month = df[df[st.session_state["date_column"]] >= last_month]
        df_last_month_sales = df_last_month.groupby(st.session_state["product_column"]).agg(
            quantity = (st.session_state["quantity_column"], "sum"),
            amount = (st.session_state["amount_column"], "mean"),
        )

        df_last_month_sales = df_last_month_sales.merge(forecast_df, on=st.session_state["product_column"], how="left")

    df_last_month_sales["difference"] = df_last_month_sales["forecast_quantity"] - df_last_month_sales["quantity"]
    df_last_month_sales["difference_percentage"] = df_last_month_sales["difference"]/df_last_month_sales["quantity"]
    
    df_last_month_sales = df_last_month_sales.sort_values(by="quantity", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_last_month_sales[st.session_state["product_column"]],
        y=df_last_month_sales[st.session_state["quantity_column"]],
        name="Last month demand"
    ))

    fig.add_trace(go.Bar(
        x=df_last_month_sales[st.session_state["product_column"]],
        y=df_last_month_sales["forecast_quantity"],
        name="Forecast demand"
    ))

    return fig

def optimized_sales_inventory_plot(forecast_venta_optimizada, prev_month_sales):
    crecimiento = ((forecast_venta_optimizada - prev_month_sales) / prev_month_sales) * 100
    crecimiento_esperado = "{:.2f}%".format(crecimiento)
    
    if crecimiento > 0:
        crecimiento_esperado = f"El crecimiento esperado es de {crecimiento_esperado}"
    else:
        crecimiento_esperado = f"El decrecimiento esperado es de {crecimiento_esperado}"

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=forecast_venta_optimizada,
        number = {'prefix': "$"},
        title={
            "text": f"""
            Forecast de venta con inventario optimizado
            <br>
            <span style='font-size:0.8em;color:gray'>
            Comparado contra la venta del mes anterior de {locale.currency(prev_month_sales, grouping=True)}
            </span>
            <br>
            <span style='font-size:0.8em;color:gray'>
            {crecimiento_esperado}
            </span>
            """
        },
        delta={"reference": prev_month_sales, "relative": True},
        domain={"x": [0, 1], "y": [0, 1]},
    ))

    fig.update_traces(delta_valueformat=".2%")

    return fig