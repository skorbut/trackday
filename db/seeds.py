from app import app, db
from app.models import Car, Racer


@app.cli.command()
def seed():
    "Adds seed data to the database."
    app.logger.info('Seeding database with sample data')
    app.logger.info('Adding cars..')
    db.session.add(
        Car(
            name='BMW M1',
            description='Carrera Digital 132 BMW M1 Procar Lotus Martini Mario Andretti Nr.1 1979',
            order_number='30814',
            image_link='https://slotcardatenbank.de/car/30814_1851/2120305396.jpeg'
        )
    )
    db.session.add(
        Car(
            name='Porsche 911 GT3 RSR',
            description='Carrera Digital 132 Porsche 911 GT3 RSR Lechner Racing Carrera Race Taxi',
            order_number='30828',
            image_link='https://slotcardatenbank.de/car/30828_2253/895352019.jpeg'
        )
    )
    db.session.add(
        Car(
            name='Mercedes-AMG GT3',
            description='Carrera Digital 132 Mercedes-AMG GT3 AKKA ASP Nr.87',
            order_number='30846',
            image_link='https://slotcardatenbank.de/car/30846_2200/1938848144.jpeg'
        )
    )
    db.session.add(
        Car(
            name='Mercedes-Benz SLS Polizei',
            description='Carrera Digital 132 Mercedes-Benz SLS AMG Polizei',
            order_number='30793',
            image_link='https://slotcardatenbank.de/car/30793_1847/1929172378.jpeg'
        )
    )
    db.session.add(
        Car(
            name='Chevrolet Corvette C7.R',
            description='Carrera Digital 132 Chevrolet Corvette C7.R Corvette Racing Nr.3',
            order_number='30701',
            image_link='https://slotcardatenbank.de/car/30701_874/58602446.jpeg'
        )
    )

    app.logger.info('Registering Racers..')
    db.session.add(Racer(name='Mika'))
    db.session.add(Racer(name='Papa'))

    db.session.commit()
    app.logger.info('..finished')
