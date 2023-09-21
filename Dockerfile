# Use an official Python runtime based on Alpine as a parent image (build stage)
FROM python:3.9-alpine as build

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY app/requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory content into the container at /app
COPY app/ ./

# Use a second, minimal parent image to reduce the final image size (production stage)
FROM python:3.9-alpine

# Copy the installed packages from the build stage
COPY --from=build /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/

# Copy the app from the build stage
COPY --from=build /app /app

# Set the working directory
WORKDIR /app

# Make port 80 and 5000 available to the world outside this container
EXPOSE 80 5000

# Run the application
CMD ["python", "main.py"]