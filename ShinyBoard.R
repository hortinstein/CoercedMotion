library(shiny)
library(plotly)
library(DT)
library(dplyr)
library(lubridate)



generate_plane_movements <- function(previous_df=NULL) {
  titles <- c("Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet")
  plane_types <- c("A320", "B737", "A380", "B747", "Cessna", "Embraer", "Bombardier")
  
  if (is.null(previous_df)) {
    # Initial data frame generation
    num_rows <- sample(seq(10, length(titles)), 1)
    df <- data.frame(
      title = sample(titles, num_rows),
      lat = runif(num_rows, -90, 90),
      lon = runif(num_rows, -180, 180),
      timestamp = Sys.time() - lubridate::minutes(sample(0:120, num_rows, replace = TRUE)),
      plane_type = sample(plane_types, num_rows, replace = TRUE)
    )
  } else {
    # Modify the existing data frame
    df <- previous_df
    df$lat <- df$lat + runif(nrow(df), -0.5, 0.5)
    df$lon <- df$lon + runif(nrow(df), -0.5, 0.5)
    df$timestamp <- Sys.time() - lubridate::minutes(sample(0:120, nrow(df), replace = TRUE))
  }
  
  # Simulate add/remove 5% of data
  changes <- max(1, as.integer(0.05 * nrow(df)))
  for (i in seq_len(changes)) {
    if (runif(1) < 0.5 && length(setdiff(titles, df$title)) > 0) {
      # Add a new row
      new_row <- data.frame(
        title = sample(setdiff(titles, df$title), 1),
        lat = runif(1, -90, 90),
        lon = runif(1, -180, 180),
        timestamp = Sys.time() - lubridate::minutes(sample(0:120, 1)),
        plane_type = sample(plane_types, 1)
      )
      df <- rbind(df, new_row)
    } else if (nrow(df) > 1) {
      # Remove a row
      df <- df[-sample(seq_len(nrow(df)), 1), ]
    }
  }
  
  return(df)
}


# Initialize global variables
previous_df <- generate_plane_movements(NULL)
flight_data <- list()  # List to track flight data

ui <- fluidPage(
  # Map and DataTable layout
  fluidRow(
    column(width = 6, plotlyOutput("live_map")),
    column(width = 6, DTOutput("live_data_table"))
  ),
  fluidRow(DTOutput("tracking_table"))
  # Interval component is now inside the server function
)

server <- function(input, output, session) {
  # Interval component for updating content
  autoInvalidate <- reactiveTimer(5000)
  
  # Function to read data
  read_data_from_csv <- function() {
    global <- .GlobalEnv
    global$previous_df <- generate_plane_movements(global$previous_df)
    global$previous_df
  }
  
  # Render the map
  output$live_map <- renderPlotly({
    autoInvalidate()
    current_df <- read_data_from_csv()
    plot_ly(current_df, x = ~lon, y = ~lat, text = ~title, mode = "markers", type = "scattermapbox") %>%
      layout(mapbox = list(style = "open-street-map", zoom = 1, center = list(lat = 20, lon = 0)))
  })
  
  # Render the data table
  output$live_data_table <- renderDT({
    autoInvalidate()
    current_df <- read_data_from_csv()
    datatable(current_df)
  })
  
  # Render the tracking table
  output$tracking_table <- renderDT({
    autoInvalidate()
    tracking_df <- data.frame(matrix(unlist(flight_data), nrow=length(flight_data), byrow=T))
    datatable(tracking_df)
  })
}

shinyApp(ui = ui, server = server)
